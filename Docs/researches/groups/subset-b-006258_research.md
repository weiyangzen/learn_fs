# subset-b-006258 Research

Grouped research report for the requested source-tree-aligned files. Each section title preserves the original source path and each section is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/spi.c -->
# sources/distributed-fs/ceph-client/net/nfc/nci/spi.c

## Purpose

This file implements the NFC Controller Interface (NCI) SPI link layer used by NFC controller drivers that expose an SPI transport. It is not a full NCI device driver; it provides reusable send, read, CRC, acknowledge, and allocation helpers around `struct nci_spi` so hardware-specific SPI drivers can move framed NCI packets between the SPI controller and the NCI core.

## Important APIs, Types, and Functions

The exported API is `nci_spi_send()`, `nci_spi_allocate_spi()`, and `nci_spi_read()`. `nci_spi_allocate_spi()` allocates a devm-managed `struct nci_spi`, stores the SPI device, NCI device, acknowledge mode, transfer delay, default controller speed, and initializes `req_completion`. `nci_spi_send()` prepends the four-byte NCI SPI header, optionally appends CRC-CCITT, optionally performs a write-handshake chip-select pulse, sends the skb with `spi_sync()`, and waits for an ACK/NACK when CRC acknowledge mode is enabled. `nci_spi_read()` receives an SPI frame, validates CRC when enabled, completes a pending send request when an ACK/NACK frame is observed, sends ACK/NACK responses, and returns only data payload skbs.

Internal helpers include `__nci_spi_send()` for one SPI transfer, `send_acknowledge()` for ACK/NACK frames, `__nci_spi_read()` for direct-read request plus response transfer, `nci_spi_check_crc()` for CRC validation and trimming, and `nci_spi_get_ack()` for parsing and stripping the SPI response header.

## Control Flow

Transmit flow starts with an NCI skb from the caller. The function pushes the SPI header, appends CRC if `NCI_SPI_CRC_ENABLED`, optionally raises chip select with a zero-length transfer and waits up to one second for a hardware completion, then writes the frame. In acknowledged mode it reinitializes `req_completion` and waits up to `NCI_SPI_SEND_TIMEOUT` for `nci_spi_read()` to observe ACK or NACK from the controller.

Receive flow issues `NCI_SPI_DIRECT_READ`, reads the two-byte response header, derives payload length with or without the CRC length, reads the remaining bytes, and, in CRC mode, pushes the response header back onto the skb so CRC covers the complete frame. After validation it strips header and CRC, completes blocked senders for ACK/NACK-only frames, and returns NULL for pure acknowledge frames.

## State and Persistence

State is held in `struct nci_spi`: acknowledge mode, SPI delay/speed, device pointers, `req_completion`, and `req_result`. There is no durable persistence. Lifetime is tied to the SPI device through devm allocation. Skbs are consumed by send/read paths and freed on completion or error.

## Dependencies and Integration Points

The file depends on Linux SPI core, skb helpers, `crc_ccitt()`, and NCI core allocation constants. It exports symbols for concrete NCI SPI drivers. It integrates with hardware interrupt/handshake logic through an optional completion supplied to `nci_spi_send()` and with the NCI core by allocating skbs against `nspi->ndev`.

## Risks and Edge Cases

Length parsing trusts controller-provided response length after a minimal header read, so allocation pressure and malformed-device behavior matter. CRC mode is critical: bad CRC sends NACK and drops the skb, while ACK/NACK-only frames unblock senders without delivering data. `wait_for_completion_interruptible_timeout()` treats interruption, timeout, and NACK as `-EIO`, which can hide the exact cause. The zero-length chip-select trick depends on controller driver tolerance for a non-NULL buffer with length zero.

## Test Signals

Useful tests include loopback or mocked SPI transfers covering CRC enabled/disabled modes, ACK, NACK, timeout, interrupted wait, malformed CRC, zero-length ACK frames, payload frames with ACK side effects, and write-handshake timeout. Runtime signals are `spi_sync()` errors, send return codes, and correct completion of pending requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/uart.c -->
# sources/distributed-fs/ceph-client/net/nfc/nci/uart.c

## Purpose

This file implements the `N_NCI` tty line discipline and the generic NCI-over-UART transport framework. It lets controller-specific UART drivers register an `nci_uart` template, attach it to a tty through `NCIUARTSETDRIVER`, queue NCI frames for tty output, and parse byte-stream input into complete NCI packets for the driver receive callback.

## Important APIs, Types, and Functions

The public driver API is `nci_uart_register()`, `nci_uart_unregister()`, and `nci_uart_set_config()`. Registration validates mandatory callbacks (`open`, `recv`, `close`), installs `nci_uart_send()` as the transport send callback, and stores the template in `nci_uart_drivers[]`. `nci_uart_set_config()` updates tty baud and RTS/CTS flow control. The line discipline is represented by `nci_uart_ldisc` with open, close, receive, write wakeup, ioctl, and no-op read/write methods.

Key internal functions are `nci_uart_set_driver()` for per-tty allocation and driver open, `nci_uart_write_work()` for draining queued skbs to `tty->ops->write`, `nci_uart_tx_wakeup()` for serialized scheduling, and `nci_uart_default_recv_buf()` for assembling byte-stream input into NCI frames using `NCI_CTRL_HDR_SIZE` and `nci_plen()`.

## Control Flow

Opening the line discipline initializes tty state and flushes pending bytes. User space then selects a registered driver with `NCIUARTSETDRIVER`; the code copies the registered template into a new per-tty `struct nci_uart`, initializes queues/work/locks, calls the driver's `open()`, and pins the module. Transmit callers enqueue skbs and schedule write work. The worker calls optional `tx_start`, writes until the tty refuses more bytes or the queue empties, preserves a partially written skb in `tx_skb`, and calls optional `tx_done` when empty.

Receive flow is entered from `receive_buf`. It serializes parsing with `rx_lock`, allocates an NCI skb once a packet starts, reads the three-byte control header, computes total packet length from the payload length, copies chunks until complete, then hands the skb to `nu->ops.recv()`.

## State and Persistence

Per-tty state includes `tx_q`, `tx_skb`, `tx_state` bits, `rx_skb`, `rx_packet_len`, `write_work`, `rx_lock`, and the attached tty/device pointers. State is volatile and destroyed on line discipline close, which purges queues, frees partial RX/TX skbs, calls driver close, drops the module reference, cancels pending work, and frees the instance.

## Dependencies and Integration Points

This code integrates the tty subsystem, NCI core skb allocation, NFC logging, and controller-specific NCI UART drivers. User space interacts only through tty line discipline selection and ioctl; normal tty read/write are disabled.

## Risks and Edge Cases

Partial writes rely on the tty driver returning a sane length. The write worker sets `TTY_DO_WRITE_WAKEUP`; broken tty wakeups can stall output until another trigger. RX parsing assumes standard unframed NCI packets; drivers needing other framing must handle it through their registered callbacks. Close ordering is important: queued skbs are freed before `cancel_work_sync()`, but the worker can still run until cancellation completes.

## Test Signals

Tests should cover driver registration collisions, ioctl before/after attachment, partial tty writes, wakeup rescheduling, close while TX is active, receive of fragmented headers and multiple packets in one buffer, corrupted receive callback return, and baud/flow-control termios changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/netlink.c -->
# sources/distributed-fs/ceph-client/net/nfc/netlink.c

## Purpose

This file is the NFC generic-netlink control and event plane. It exposes device, target, LLCP, firmware, secure element, DEP link, polling, and vendor command operations to user space, and emits multicast events when NFC device state changes.

## Important APIs, Types, and Functions

The core object is `nfc_genl_family`, configured with `nfc_genl_policy`, one multicast event group, and `nfc_genl_ops[]`. Command handlers include `nfc_genl_get_device()`, `nfc_genl_dev_up()`, `nfc_genl_dev_down()`, `nfc_genl_start_poll()`, `nfc_genl_stop_poll()`, target activation/deactivation, DEP link up/down, LLCP parameter get/set and SDP request, firmware download, secure element enable/disable/get/IO, and vendor command dispatch.

Event helpers include `nfc_genl_targets_found()`, `nfc_genl_target_lost()`, `nfc_genl_device_added()`, `nfc_genl_device_removed()`, `nfc_genl_dep_link_up_event()`, `nfc_genl_dep_link_down_event()`, target-mode activated/deactivated events, LLCP service discovery responses, secure element add/remove/transaction/connectivity events, and firmware-download completion.

Vendor support is built around `nfc_genl_vendor_cmd()`, `__nfc_alloc_vendor_cmd_reply_skb()`, and `nfc_vendor_cmd_reply()`, using `dev->cur_cmd_info` to route replies to the triggering request.

## Control Flow

Request handlers parse required attributes, obtain `struct nfc_dev` with `nfc_get_device()`, call the NFC core operation, then put the device. Operations that mutate polling ownership use `dev->genl_data.genl_data_mutex`; target and LLCP operations often take `device_lock(&dev->dev)`. Dump operations retain iteration state in `netlink_callback->args`, use device generation counters for consistency, and release references in `.done` callbacks.

Multicast event helpers allocate a netlink skb, emit command-specific attributes, end the generic-netlink message, then multicast on the NFC family event group. Secure element IO is asynchronous: the request allocates `se_io_ctx`, validates device/up/SE state in `nfc_se_io()`, passes a callback to the driver, and `se_io_cb()` later multicasts APDU output and frees the context.

The netlink notifier listens for `NETLINK_URELEASE`. If the process that started polling disappears, scheduled work iterates NFC devices and stops polling for matching `poll_req_portid`.

## State and Persistence

Persistent kernel state lives mostly in `struct nfc_dev`: device index, target arrays/generation, polling state, DEP state, secure element list, vendor command table, and `genl_data.poll_req_portid`. This file initializes and destroys only the per-device generic-netlink mutex and tracks no durable storage.

## Dependencies and Integration Points

The file depends on generic netlink, public NFC uapi definitions, the local NFC core header, and LLCP internals. It is the user-space ABI endpoint for NFC daemons and tools. It also bridges vendor driver callbacks and NFC core functions such as `nfc_start_poll()`, `nfc_activate_target()`, `nfc_fw_download()`, and `nfc_enable_se()`.

## Risks and Edge Cases

Many operations intentionally use relaxed legacy validation flags, so per-command attribute checks are the main protection. Poll ownership is tied to netlink portid; incorrect cleanup could leave polling active. LLCP SDP request building must free partial TLV lists on all errors. Vendor replies depend on `dev->cur_cmd_info` being set only during command execution. Event allocation failures generally drop events with `-ENOMEM` or `-EMSGSIZE`, so userspace must tolerate missed notifications.

## Test Signals

Exercise each command with missing, malformed, and valid attributes; verify admin-only flags for mutating commands; test dumps across multiple devices/targets/secure elements; test poll start then netlink socket release; validate LLCP parameter bounds and SDP nested parsing; test SE IO callback success and error paths; verify vendor command dispatch/reply and unsupported vendor returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nfc.h -->
# sources/distributed-fs/ceph-client/net/nfc/nfc.h

## Purpose

This private NFC header declares internal types, constants, helpers, and cross-file entry points for the kernel NFC subsystem. It connects raw sockets, generic netlink, LLCP, AF_NFC protocol registration, and the core NFC device lifecycle without exposing these internals as public uapi.

## Important APIs, Types, and Functions

The header defines target mode constants `NFC_TARGET_MODE_IDLE` and `NFC_TARGET_MODE_SLEEP`, `struct nfc_protocol` for AF_NFC protocol registration, `struct nfc_rawsock` for raw/seqpacket socket state, and `struct nfc_sock_list` for protected socket lists. Accessors include `nfc_rawsock()`, `to_rawsock_sk()`, `nfc_put_device()`, and class iterator helpers.

Declarations cover LLCP MAC notifications, LLCP device registration, remote/general bytes, data receive, local lookup/refcounting, SDP TLV cleanup, raw socket init/exit, AF_NFC init/exit and protocol registration, netlink init/exit and event emitters, device lookup, firmware download, device up/down, polling, DEP link management, target activation/deactivation, data exchange, and secure element enable/disable.

## Control Flow

This header itself has no runtime control flow. Its value is in defining the callable graph among NFC compilation units. For example, `rawsock.c` uses `nfc_get_device()`, target activation, and data exchange declarations; `netlink.c` uses LLCP and core device functions; NFC device code can call the netlink event emitters declared here.

## State and Persistence

The state shape declared here includes `nfc_rawsock` fields for connected device pointer, target index, transmit work, and scheduling flag, plus socket list locking. External declarations for `nfc_devlist_generation` and `nfc_devlist_mutex` describe shared device-list state maintained elsewhere. There is no persistence beyond kernel object lifetime.

## Dependencies and Integration Points

It includes `<net/nfc/nfc.h>` and `<net/sock.h>` and is included by NFC internal C files. It is the integration seam between NFC core, LLCP, generic netlink, raw sockets, and protocol registration.

## Risks and Edge Cases

Because this header centralizes internal prototypes, mismatched lifetime assumptions can spread across files. `nfc_put_device()` is a simple `put_device()` wrapper, so callers must hold valid references. Socket-state macros rely on `struct nfc_rawsock` embedding `struct sock` as the first member.

## Test Signals

Compile coverage with NFC, LLCP, raw sockets, and netlink enabled is the main signal. Runtime tests should verify that declared lifecycle pairings are balanced: init/exit, get/put device, LLCP local get/put, and AF_NFC protocol register/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nfc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/rawsock.c -->
# sources/distributed-fs/ceph-client/net/nfc/rawsock.c

## Purpose

This file implements the AF_NFC raw socket protocol. It supports connected `SOCK_SEQPACKET` sockets for exchanging data with an activated NFC target and privileged `SOCK_RAW` sockets for passively receiving raw NFC traffic copies with metadata headers.

## Important APIs, Types, and Functions

The protocol is registered by `rawsock_init()` through `nfc_proto_register()` with `rawsock_nfc_proto`. The main socket operations are `rawsock_create()`, `rawsock_connect()`, `rawsock_release()`, `rawsock_sendmsg()`, and `rawsock_recvmsg()`. Monitor delivery is exported as `nfc_send_to_raw_sock()`.

`rawsock_tx_work()` asynchronously dequeues outgoing skbs and calls `nfc_data_exchange()`. `rawsock_data_exchange_complete()` adds the one-byte NFC header to replies, queues them to the socket receive queue, and schedules the next transmit if more data is queued. `rawsock_destruct()` deactivates the target and drops the NFC device reference for established sockets.

## Control Flow

`rawsock_create()` accepts only `SOCK_SEQPACKET` and `SOCK_RAW`. Raw sockets require `CAP_NET_RAW`, use receive-only ops, and are linked into `raw_sk_list`; seqpacket sockets initialize transmit work. `rawsock_connect()` validates the NFC sockaddr, gets the target device, checks target index against the current target range, activates the target for the requested protocol, stores the device and target index, and moves the socket to connected state.

`sendmsg()` allocates an NFC send skb, copies user payload, appends it to `sk_write_queue`, and schedules TX work if idle. Completion queues the response and continues the TX queue. Release unlinks raw sockets and, for connected sockets, sets send shutdown, cancels TX work, purges queued writes, orphans the socket, and drops the socket reference.

## State and Persistence

Per-socket state is embedded in `struct nfc_rawsock`: `dev`, `target_idx`, `tx_work`, and `tx_work_scheduled`. Raw monitor sockets are tracked in a global hlist with rwlock. There is no durable persistence; target activation persists only while the socket remains established.

## Dependencies and Integration Points

The file depends on AF_NFC protocol registration, NFC core target activation/data exchange/deactivation, socket and skb datagram helpers, kcov remote coverage, and Linux capability checks. `nfc_send_to_raw_sock()` is called by lower NFC paths to fan out observed traffic to raw monitors.

## Risks and Edge Cases

Release/work ordering is safety-critical because TX work uses the NFC device pointer. The code sets `SEND_SHUTDOWN`, cancels work synchronously, and purges the write queue before orphaning to avoid use-after-free. `rawsock_tx_work()` assumes `skb_dequeue()` returns a valid skb when scheduled. Raw monitor fanout clones one prepared skb per socket; allocation failures silently skip recipients.

## Test Signals

Tests should cover capability enforcement, invalid sockaddr/target ranges, connect while connected, send before connect, queued multi-message exchange, data-exchange error propagation, release during active exchange, raw monitor fanout header fields, and receive truncation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/rawsock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nsh/Kconfig -->
# sources/distributed-fs/ceph-client/net/nsh/Kconfig

## Purpose

This Kconfig file defines the `NET_NSH` build option for Linux Network Service Header support. It documents that the implementation targets Service Function Chaining per RFC 7665 and currently supports MD type 1 only, primarily for Open vSwitch integration.

## Important APIs, Types, and Functions

There are no C APIs in this file. The important symbol is `NET_NSH`, a tristate menuconfig option titled "Network Service Header (NSH) protocol" with default `n`.

## Control Flow

At configuration time, enabling `NET_NSH` causes `net/nsh/Makefile` to build `nsh.o`. Open vSwitch selects this symbol when OVS is enabled, making NSH push/pop helpers available to OVS actions.

## State and Persistence

The only persistent state is the kernel build configuration choice. No runtime state is defined here.

## Dependencies and Integration Points

The help text identifies Open vSwitch as the current consumer. `net/openvswitch/Kconfig` selects `NET_NSH`, and `nsh.c` exports helper symbols used by OVS action execution.

## Risks and Edge Cases

The help text narrows support to MD type 1 and Open vSwitch. Users expecting generic NSH handling or other metadata types may overestimate the feature.

## Test Signals

Configuration tests should verify that selecting Open vSwitch selects `NET_NSH`, that `NET_NSH=m/y` builds `nsh.o`, and that disabling it removes NSH protocol object compilation unless selected by a dependent feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nsh/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nsh/Makefile -->
# sources/distributed-fs/ceph-client/net/nsh/Makefile

## Purpose

This Makefile wires the NSH protocol implementation into the kernel build.

## Important APIs, Types, and Functions

The only build rule is `obj-$(CONFIG_NET_NSH) += nsh.o`, which compiles and links `nsh.c` when `NET_NSH` is built-in or modular.

## Control Flow

Kbuild evaluates `CONFIG_NET_NSH` and includes `nsh.o` in the corresponding built-in or module object list. Runtime init is handled by `nsh.c`.

## State and Persistence

The file has no runtime state. It reflects build configuration state only.

## Dependencies and Integration Points

It depends directly on the Kconfig symbol defined in the same directory and indirectly supports Open vSwitch's NSH actions by building exported helper functions.

## Risks and Edge Cases

There are no conditional sub-objects or flags, so all NSH behavior is bundled into one object. Build failures in `nsh.c` affect the entire `NET_NSH` option.

## Test Signals

Build matrix signals are sufficient: `CONFIG_NET_NSH=n` omits `nsh.o`; `m` produces a module object; `y` links the code built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nsh/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nsh/nsh.c -->
# sources/distributed-fs/ceph-client/net/nsh/nsh.c

## Purpose

This file implements Linux Network Service Header packet manipulation and GSO support. It exports `nsh_push()` and `nsh_pop()` for consumers such as Open vSwitch, and registers a packet offload handler for `ETH_P_NSH` segmentation.

## Important APIs, Types, and Functions

`nsh_push()` prepends an NSH header to an skb, derives the old payload protocol as a tunnel protocol (`TUN_P_ETHERNET` or `tun_p_from_eth_p()`), copies the requested header, fills `nh->np`, updates checksum, resets skb protocol and headers to `ETH_P_NSH`, and clears MAC length. `nsh_pop()` validates and pulls an NSH header, maps `nh->np` back to an Ethernet protocol with `tun_p_to_eth_p()`, updates checksum/header offsets, and restores `skb->protocol`.

`nsh_gso_segment()` temporarily removes the NSH header, segments the inner packet with `skb_mac_gso_segment()`, then pushes outer headers back onto each segment. Module init/exit register and unregister `nsh_packet_offload`.

## Control Flow

Push/pop are synchronous skb transforms used by callers in packet action paths. GSO flow starts when the stack segments an `ETH_P_NSH` skb. The code validates base and full NSH length, maps the next protocol, pulls the NSH header, sets inner MAC/protocol state for segmentation, and either unwinds on error or restores outer NSH framing on each generated segment.

## State and Persistence

Runtime state is limited to the registered `packet_offload` descriptor. Packet state changes are carried in skb headers, protocol fields, checksum state, and header offsets. No durable storage exists.

## Dependencies and Integration Points

The file depends on `net/nsh.h`, skb GSO helpers, tunnel protocol mapping helpers, and packet offload registration. Open vSwitch action execution uses the exported push/pop helpers for `OVS_ACTION_ATTR_PUSH_NSH` and `OVS_ACTION_ATTR_POP_NSH`.

## Risks and Edge Cases

Header length validation is essential: a header shorter than `NSH_BASE_HDR_LEN` returns `-EINVAL`, while insufficient linear data returns `-ENOMEM`. Unsupported inner protocol returns `-EAFNOSUPPORT`. GSO unwind must restore protocol, header offsets, and MAC length correctly to avoid corrupting the original skb after segmentation failure.

## Test Signals

Tests should cover push/pop of Ethernet and L3 payloads, unsupported protocols, malformed length, non-linear skb pull failures, checksum correctness, GSO success for inner IPv4/IPv6/TCP traffic, and GSO error unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nsh/nsh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/Kconfig -->
# sources/distributed-fs/ceph-client/net/openvswitch/Kconfig

## Purpose

This Kconfig file defines the kernel Open vSwitch datapath options and optional tunnel vport support. It describes OVS as an in-kernel fast path for a userspace-controlled multilayer virtual switch.

## Important APIs, Types, and Functions

The primary symbol is `OPENVSWITCH`, a tristate depending on `INET` and compatible netfilter options. It selects support libraries and protocols such as MPLS, CRC32C, MPLS GSO, destination cache, NSH, and OVS-specific conntrack/NAT modules when netfilter is enabled. Optional symbols are `OPENVSWITCH_GRE`, `OPENVSWITCH_VXLAN`, and `OPENVSWITCH_GENEVE`, each depending on `OPENVSWITCH` and its tunnel subsystem.

## Control Flow

At kernel configuration time, selecting `OPENVSWITCH` enables the main module build and selects dependencies. Tunnel options default to `OPENVSWITCH`, so they follow the main datapath unless explicitly disabled.

## State and Persistence

The file defines build-time configuration only. Runtime datapath, vport, flow, and conntrack state are implemented in C files.

## Dependencies and Integration Points

The dependency expression ensures OVS is built only with compatible netfilter conntrack, NAT, defrag, and conncount availability. The selects wire OVS to NSH, MPLS, conntrack, NAT, and tunnel modules used by actions and vports.

## Risks and Edge Cases

The netfilter dependency expression is subtle: configurations with partial conntrack/NAT support can alter available OVS action behavior. Because tunnel options default on, binary size and exposed vport types may be larger than expected unless disabled.

## Test Signals

Configuration tests should validate OVS with and without NF_CONNTRACK/NF_NAT/NETFILTER_CONNCOUNT, and ensure tunnel symbols produce the corresponding `vport-*.o` objects. Build tests should cover built-in and module combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/Makefile -->
# sources/distributed-fs/ceph-client/net/openvswitch/Makefile

## Purpose

This Makefile defines the Open vSwitch module composition and optional vport objects.

## Important APIs, Types, and Functions

The main object is `openvswitch.o`, built from action execution, datapath control, notification, flow parsing/table, meter, tracing, and vport source files. `conntrack.o` is added when `CONFIG_NF_CONNTRACK` is set. Optional tunnel modules are `vport-vxlan.o`, `vport-geneve.o`, and `vport-gre.o`. The trace object gets `-I$(src)`.

## Control Flow

Kbuild combines `openvswitch-y` into `openvswitch.o` for `CONFIG_OPENVSWITCH`. Optional object lines attach tunnel implementations to their own configuration symbols.

## State and Persistence

No runtime state is represented here. The file determines which code is present in the compiled kernel/module.

## Dependencies and Integration Points

It mirrors Kconfig feature gates and ensures datapath code is linked with flow, meter, vport, and tracing subsystems. Conditional conntrack inclusion matches the stubs in `conntrack.h`.

## Risks and Edge Cases

Feature mismatches can happen if callers assume conntrack or tunnel actions exist when their object was not built. Trace include flags are local to `openvswitch_trace.o`.

## Test Signals

Build tests should verify `openvswitch.o` composition with conntrack enabled/disabled and each tunnel option as built-in/module/off. Symbol tests should ensure `ovs_ct_*` references resolve to real code or stubs according to configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/actions.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/actions.c

## Purpose

This file is the Open vSwitch datapath action executor. It applies validated netlink action lists to skbs, including output, userspace upcalls, packet header mutation, tunnel metadata, VLAN/MPLS/Ethernet/NSH encapsulation, conntrack, metering, sampling, cloning, recirculation, packet length branching, TTL decrement, drop, and psample.

## Important APIs, Types, and Functions

The exported entry point is `ovs_execute_actions()`. It manages recursion depth in per-CPU `ovs_pcpu_storage`, calls `do_execute_actions()`, and drains deferred actions at top level. `do_execute_actions()` is the central action switch. Header mutation helpers include `push_mpls()`, `pop_mpls()`, `set_mpls()`, `push_vlan()`, `pop_vlan()`, `set_eth_addr()`, `push_eth()`, `pop_eth()`, `push_nsh()`, `pop_nsh()`, `set_ipv4()`, `set_ipv6()`, `set_udp()`, `set_tcp()`, and `set_sctp()`.

Action composition helpers include `clone_execute()`, `sample()`, `clone()`, `execute_recirc()`, `execute_check_pkt_len()`, and `process_deferred_actions()`. Output helpers include `do_output()`, `ovs_fragment()`, `prepare_frag()`, `ovs_vport_output()`, and `output_userspace()`.

## Control Flow

`ovs_execute_actions()` increments execution level, rejects excessive recursion, records original action length, and dispatches each action. Last output-like actions consume the skb directly; non-last output actions clone it. Packet mutations update checksums, skb hash, conntrack state, and the cached `sw_flow_key` when possible. Encapsulation changes invalidate the cached flow key so later recirculation recomputes it.

Recirculation and nested clone/sample/check-packet-length actions either execute immediately using cloned per-CPU flow keys or enqueue a `deferred_action` when nesting exceeds available key slots. Top-level execution drains the FIFO afterward. Conntrack actions ensure the flow key is current, call `ovs_ct_execute()`, and hide stolen fragments by mapping `-EINPROGRESS` to success.

## State and Persistence

State is per packet (`skb`, `OVS_CB`, `sw_flow_key`) and per CPU (`exec_level`, deferred action FIFO, cloned keys, fragmentation scratch). There is no durable storage. Packet output can change device state only through vport send paths outside this file.

## Dependencies and Integration Points

The executor depends on `datapath.h`, flow key helpers, vports, meters, conntrack, NSH, MPLS, GSO/fragmentation, checksum helpers, psample, and OVS tracepoints. It is called from datapath packet hits and userspace packet execute commands.

## Risks and Edge Cases

Action ordering and skb ownership are critical: many actions consume or free the skb on last action or error. Header mutations must keep checksums and cached keys consistent. Deferred action FIFO and recursion limits prevent unbounded nested clone/recirc but can drop packets. Fragmentation reconstructs L2 state from per-CPU scratch and must not exceed `MAX_L2_LEN`. Conntrack clearing on address/port changes avoids stale `_nfct`.

## Test Signals

High-value tests cover every action type, nested clone/sample/recirc limits, key invalidation and recomputation, checksum correctness after masked sets, conntrack interactions after NAT or address mutation, output truncation/cutlen, MRU fragmentation paths, TTL exception actions, psample metadata, and packet ownership on error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/actions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/conntrack.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/conntrack.c

## Purpose

This file integrates Open vSwitch actions and flow keys with Linux netfilter conntrack, NAT, helpers, labels, marks, timeouts, event masks, and optional per-zone connection limits. It handles both control-plane parsing/serialization of OVS CT actions and packet-time execution of tracking and commit operations.

## Important APIs, Types, and Functions

The central action state is `struct ovs_conntrack_info`, containing helper, zone, template conntrack, commit/force/nat flags, family, event mask, mark/labels, timeout, timeout extension, and optional NAT range. Public functions include `ovs_ct_init()`, `ovs_ct_exit()`, `ovs_ct_verify()`, `ovs_ct_copy_action()`, `ovs_ct_action_to_attr()`, `ovs_ct_execute()`, `ovs_ct_clear()`, `ovs_ct_fill_key()`, `ovs_ct_put_key()`, and `ovs_ct_free_action()`.

Packet execution flows through `ovs_ct_execute()`, `__ovs_ct_lookup()`, `ovs_ct_lookup()`, and `ovs_ct_commit()`. Parsing uses `parse_ct()` and `parse_nat()`. Key update helpers include `ovs_ct_update_key()`, `__ovs_ct_update_key()`, `ovs_nat_update_key()`, and original tuple helpers. Optional conncount support defines `ovs_ct_limit_info`, zone limit hash manipulation, CT limit generic-netlink commands, and `dp_ct_limit_genl_family`.

## Control Flow

`ovs_ct_copy_action()` validates the packet family, parses nested CT attributes, allocates an nf_conntrack template for the selected zone, attaches timeout/helper state, stores the action in the flow action list, and marks templates confirmed when commit is requested. At packet time, `ovs_ct_execute()` pulls the skb to L3, trims network payload, defragments if needed, then calls lookup or commit. Lookup avoids duplicate conntrack work when cached state matches; otherwise it installs the zone template and calls `nf_conntrack_in()`.

If a connection exists, the code conditionally performs NAT, attaches helpers on commit, invokes helpers, makes TCP established tracking liberal, fills action extensions, and updates `sw_flow_key` CT fields. Commit applies event masks, mark, labels, conncount limits, and confirms the connection. NAT updates flow-key addresses/ports after translation.

## State and Persistence

Persistent state is in netfilter conntrack tables, conntrack labels/marks/timeouts, helper references, and optional per-net OVS CT limit tables. Per-action state is copied into flow actions and freed by `ovs_ct_free_action()`. Per-net initialization acquires connlabel capacity and initializes conncount data when enabled.

## Dependencies and Integration Points

The file depends heavily on netfilter conntrack core, zones, labels, helpers, timeouts, NAT, defrag, and conncount. It integrates with OVS flow netlink parsing, datapath per-net state, flow keys, and the action executor.

## Risks and Edge Cases

Conntrack state caching is subtle: stale `_nfct`, NAT direction inversion, forced commit, zone mismatch, helper mismatch, or timeout mismatch all force fresh tracking or deletion. Defragmentation can steal skbs, reported as `-EINPROGRESS`. Mark/label updates are allowed only with commit. NAT attributes require commit when specifying new source/destination ranges. Optional feature stubs and Kconfig combinations change supported keys/actions.

## Test Signals

Tests should cover CT lookup and commit for IPv4/IPv6, zones, invalid packets, fragments, NAT existing and new connections, helper attachment, timeout policy, event masks, mark/label masked writes, CT clear, original tuple key emission, forced commit, recirculation with cached CT state, conncount set/get/delete and limit exceed, plus configurations without NAT, labels, marks, timeouts, or conncount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/conntrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/conntrack.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/conntrack.h

## Purpose

This header declares the Open vSwitch conntrack interface used by flow parsing, action execution, and datapath initialization. It also provides no-conntrack stubs so the rest of OVS can build when `CONFIG_NF_CONNTRACK` is disabled.

## Important APIs, Types, and Functions

When conntrack is enabled, the header declares lifecycle (`ovs_ct_init`, `ovs_ct_exit`), attribute verification (`ovs_ct_verify`), action parse/serialize/free (`ovs_ct_copy_action`, `ovs_ct_action_to_attr`, `ovs_ct_free_action`), packet execution (`ovs_ct_execute`, `ovs_ct_clear`), and flow key helpers (`ovs_ct_fill_key`, `ovs_ct_put_key`). It defines `CT_SUPPORTED_MASK` as the set of OVS CT state bits available to matching.

When conntrack is disabled, inline stubs return `-ENOTSUPP`, clear CT key fields, or free/drop skbs as appropriate. If conncount is enabled, it also declares `dp_ct_limit_genl_family`.

## Control Flow

The header has compile-time control flow via `#if IS_ENABLED(CONFIG_NF_CONNTRACK)`. Call sites can use the same function names independent of configuration; either the real implementation in `conntrack.c` or stubs are compiled.

## State and Persistence

No state is owned here. The declarations describe per-net conntrack initialization and flow-key CT fields. Disabled stubs explicitly zero `ct_state`, `ct_zone`, `ct.mark`, labels, and `ct_orig_proto` so keys remain deterministic.

## Dependencies and Integration Points

It includes `flow.h` and is included by datapath and action code. It is the feature boundary between core OVS and netfilter conntrack.

## Risks and Edge Cases

The disabled `ovs_ct_execute()` stub frees the skb before returning `-ENOTSUPP`; callers must not continue to use the skb. Feature availability is compile-time dependent, so userspace must handle action rejection when conntrack is unavailable.

## Test Signals

Build tests with `CONFIG_NF_CONNTRACK=y/m/n` should validate real/stub symbol selection. Runtime tests without conntrack should verify CT actions are rejected during action validation and CT key fields serialize as absent/zero as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/conntrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/datapath.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/datapath.c

## Purpose

This file is the main Open vSwitch kernel datapath implementation. It registers OVS generic-netlink families, owns datapath/vport/flow/packet command handlers, processes packets through flow lookup and action execution, sends upcalls to userspace, manages per-net datapath lifecycle, and initializes/cleans up the module.

## Important APIs, Types, and Functions

Global exports include `ovs_lock()`, `ovs_unlock()`, `lockdep_ovsl_is_held()`, `ovs_dp_name()`, `ovs_lookup_vport()`, `ovs_dp_detach_port()`, `ovs_dp_process_packet()`, `ovs_dp_upcall()`, `ovs_dp_get_upcall_portid()`, and `ovs_vport_cmd_build_info()`. Generic-netlink families cover datapaths (`OVS_DATAPATH_FAMILY`), vports (`OVS_VPORT_FAMILY`), flows (`OVS_FLOW_FAMILY`), packets (`OVS_PACKET_FAMILY`), meters, and optional CT limits.

Major command handlers include `ovs_packet_cmd_execute()`, `ovs_flow_cmd_new/set/get/del/dump()`, `ovs_dp_cmd_new/set/get/del/dump()`, and `ovs_vport_cmd_new/set/get/del/dump()`. Lifecycle functions include `ovs_init_net()`, `ovs_exit_net()`, `dp_init()`, and `dp_cleanup()`.

## Control Flow

Packet receive enters `ovs_dp_process_packet()` with an extracted key and input vport. It looks up the flow table with stats, sends a miss upcall if no flow exists, or updates flow stats and executes actions on hit. Upcalls use `queue_userspace_packet()` or `queue_gso_packets()` to build `OVS_PACKET_ATTR_*` netlink messages, include key, userdata, actions, MRU, hash, and packet bytes, then unicast to the selected handler port.

Control-plane netlink commands run under `ovs_mutex` for mutations and RCU for dumps/lookups. Flow commands parse keys/masks/actions, update the flow table, support UFIDs, optionally clear stats, and notify listeners. Datapath commands create/destroy datapaths with local vports, stats, flow tables, meters, user features, and per-CPU upcall portids. Vport commands add/remove/configure ports, update datapath headroom, and report vport stats/options.

Module init allocates per-CPU storage, registers internal device links, flow/vport subsystems, per-net ops, netdevice notifier, netdev vports, generic-netlink families, and drop reasons. Cleanup unregisters in reverse and waits for RCU callbacks.

## State and Persistence

Runtime state includes per-net `struct ovs_net`, each `struct datapath`, flow tables, vport hash buckets, meters, per-CPU stats, RCU-protected per-CPU upcall pid arrays, mask rebalance delayed work, and per-CPU action storage. There is no durable persistence; userspace recreates datapaths and flows.

## Dependencies and Integration Points

This file integrates generic netlink, net namespaces, vport providers, flow parsing/table code, action execution, meters, conntrack init/exit, netdevice notifiers, tc skb extensions, and drop reason infrastructure. Userspace `ovs-vswitchd` controls it through the registered netlink families.

## Risks and Edge Cases

Locking is central: writes use `ovs_mutex`, reads use RCU, and RT packet recursion uses local locks. Upcall loss increments `n_lost`; handler portid zero drops. VLAN accelerated packets are cloned and pushed inside for userspace visibility. Feature negotiation can reset unsupported user features for old userspace. Datapath destruction must remove non-local vports before local port and flush flows before RCU free.

## Test Signals

Tests should cover packet miss/hit stats, upcall message contents, GSO segmentation upcalls, packet execute, flow add/update/delete/dump with UFID flags, datapath create/set/delete/dump, vport create/set/delete/dump, per-CPU upcall PID dispatch, mask cache resizing, namespace teardown, module init cleanup failures, and concurrent flow/vport mutations under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/datapath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/datapath.h -->
# sources/distributed-fs/ceph-client/net/openvswitch/datapath.h

## Purpose

This header defines the core Open vSwitch datapath data structures, per-skb control block, per-net state, per-CPU action scratch state, locking helpers, vport lookup helpers, and exported datapath/action interfaces used across OVS source files.

## Important APIs, Types, and Functions

Important structures include `dp_stats_percpu`, `dp_nlsk_pids`, `datapath`, `ovs_skb_cb`, `dp_upcall_info`, `ovs_net`, `ovs_frag_data`, `deferred_action`, `action_fifo`, `action_flow_keys`, and `ovs_pcpu_storage`. Constants include datapath port/hash limits, mask rebalance interval, deferred action FIFO size, recursion limit, and supported packet hash flags.

The header declares `ovs_lock()`, `ovs_unlock()`, `ovs_lookup_vport()`, `ovs_dp_process_packet()`, `ovs_dp_detach_port()`, `ovs_dp_upcall()`, `ovs_dp_get_upcall_portid()`, `ovs_dp_name()`, `ovs_vport_cmd_build_info()`, `ovs_execute_actions()`, and `ovs_dp_notify_wq()`. It also provides `OVS_CB()`, `ASSERT_OVSL()`, RCU dereference helpers, datapath net getters/setters, vport lookup wrappers, `get_dp_rcu()`, and `get_dp()`.

## Control Flow

The header has inline lookup/control helpers. `get_dp_rcu()` maps a datapath ifindex to the internal vport and datapath under RCU. `get_dp()` wraps that lookup while accepting either RCU or `ovs_mutex`. Vport accessors encode locking expectations: plain RCU, OVS lock plus RCU, or OVS lock only.

## State and Persistence

The declared state is runtime-only. `datapath` holds flow table, ports, stats, namespace, user features, max headroom, meters, and upcall pids. `ovs_net` holds per-net datapath list and maintenance work. `ovs_pcpu_storage` holds action recursion/defer state and fragmentation scratch used by `actions.c`.

## Dependencies and Integration Points

It includes conntrack, flow, flow table, meter, internal dev, skb, netdevice, and tunnel headers. It is included by most OVS implementation files and by notifier/action paths.

## Risks and Edge Cases

`OVS_CB()` overlays skb control buffer, so `datapath.c` enforces size at module init. Locking annotations must match call sites to avoid RCU misuse. The `OVS_MASKED` macro assumes the supplied key has no bits outside the mask. Per-CPU storage is shared by action recursion and fragmentation, so callers must respect execution context locking.

## Test Signals

Compile-time and lockdep coverage are important. Runtime tests should stress vport lookup during concurrent deletion, datapath namespace teardown, skb control block usage with GSO, action recursion, and per-CPU upcall PID access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/datapath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/dp_notify.c -->
# sources/distributed-fs/ceph-client/net/openvswitch/dp_notify.c

## Purpose

This file handles netdevice unregister notifications for Open vSwitch vports backed by ordinary netdevices. When an external device disappears, it schedules OVS work to detach the corresponding vport and multicast a vport deletion notification.

## Important APIs, Types, and Functions

The exported object is `ovs_dp_device_notifier`. Its callback `dp_device_event()` reacts to `NETDEV_UNREGISTER`. The workqueue function `ovs_dp_notify_wq()` scans all datapaths in the net namespace and detaches vports whose devices are no longer OVS ports. `dp_detach_port_notify()` builds the deletion netlink message with `ovs_vport_cmd_build_info()`, detaches the port, and multicasts on `dp_vport_genl_family`.

## Control Flow

On netdevice events, internal OVS devices are ignored. For non-internal devices, the callback looks up the associated vport. If the event is unregister, it immediately calls `ovs_netdev_detach_dev()` to unlink upper device state and decrement promiscuity, then queues `dp_notify_work` on `system_percpu_wq`.

The work function takes `ovs_mutex`, walks all datapaths and vport hash buckets, skips internal vports, identifies vports whose device no longer reports `netif_is_ovs_port()`, and detaches/notifies each one.

## State and Persistence

No independent durable state is owned here. It uses per-net `ovs_net->dp_notify_work`, datapath vport tables, and vport device association. Detach operations mutate datapath port membership.

## Dependencies and Integration Points

It depends on Linux netdevice notifier infrastructure, generic netlink multicast, OVS datapath helpers, internal-device helpers, and netdev vport helpers. It is registered and unregistered by `datapath.c` module lifecycle.

## Risks and Edge Cases

Detach is deferred because notifier context is not the right place to destroy the vport fully. If notification allocation fails, the port is still detached and netlink error is set for listeners. The scanner must hold `ovs_mutex` while walking and modifying vport hash lists.

## Test Signals

Tests should unregister a netdev-backed OVS port and verify immediate netdev detach, later vport deletion, multicast notification, no action for internal ports, correct behavior when notification allocation fails, and safe operation during concurrent datapath deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/openvswitch/dp_notify.c -->
