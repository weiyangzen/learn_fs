# subset-b-006196 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/socket.c -->
# sources/distributed-fs/ceph-client/net/ieee802154/socket.c

## Purpose
`socket.c` implements the AF_IEEE802154 socket family for IEEE 802.15.4 devices. It exposes two socket personalities: `SOCK_RAW` sockets that send and receive complete 802.15.4 frames, and `SOCK_DGRAM` sockets that build data-frame headers, maintain source/destination 802.15.4 addresses, and expose WPAN-specific socket options.

## Important APIs, types, and functions
The file registers `ieee802154_family_ops` through `sock_register()` and attaches `ieee802154_packet_type` to `ETH_P_IEEE802154`. `ieee802154_create()` selects `ieee802154_raw_prot`/`ieee802154_raw_ops` or `ieee802154_dgram_prot`/`ieee802154_dgram_ops`. Shared socket wrappers include `ieee802154_sock_release()`, `ieee802154_sock_sendmsg()`, `ieee802154_sock_bind()`, `ieee802154_sock_connect()`, and `ieee802154_sock_ioctl()`. Raw-socket state is tracked in `raw_head` under `raw_lock`; datagram state uses `struct dgram_sock`, `dgram_head`, and `dgram_lock`. Address resolution is centralized in `ieee802154_get_dev()`, which maps long or short IEEE 802.15.4 addresses to netdevices.

## Control flow
Module init registers both protocol objects, registers the socket family, then adds the packet handler. Socket creation rejects non-init network namespaces, requires `CAP_NET_RAW` for raw sockets, allocates a `struct sock`, installs protocol ops, hashes the socket, and runs per-protocol init. Raw sends pick a bound device or the first IEEE802154 device, copy user payload into an skb, set `ETH_P_IEEE802154`, and transmit with `dev_queue_xmit()`. Datagram sends resolve either an explicit send address or a connected destination, select the bound source device if present, fill `ieee802154_mac_cb` flags, build the MAC header via `wpan_dev_hard_header()`, append payload, and transmit. Receive flow enters `ieee802154_rcv()`, drops frames from stopped devices or non-init namespaces, clones to matching raw sockets, then delivers non-`PACKET_OTHERHOST` frames to matching datagram sockets.

## State and persistence
Socket state is volatile in-kernel state only. Raw sockets persist only their bound device index. Datagram sockets persist source and destination `struct ieee802154_addr`, bound/connected bits, ack and LQI preferences, and security override bits/levels. Global socket lists are protected by rwlocks and protocol in-use counters. No durable storage is written.

## Dependencies and integration points
The implementation depends on core socket/proto registration, netdevice lookup, `dev_add_pack()`, IEEE802154 address conversion helpers, `wpan_dev_hard_header()`, skbuff datagram helpers, capability checks, and netdevice ioctls for `SIOCGIFADDR`/`SIOCSIFADDR`. It integrates with userspace through AF_IEEE802154 socket calls and `SOL_IEEE802154` options such as `WPAN_WANTACK`, `WPAN_WANTLQI`, `WPAN_SECURITY`, and `WPAN_SECURITY_LEVEL`.

## Risks and invariants
`ieee802154_get_dev()` assumes matching `ieee802154_ptr` state on ARPHRD_IEEE802154 devices and deliberately rejects broadcast/undefined short addresses for binding. Datagram delivery queues the original skb to the last matching socket and clones for earlier matches, so clone allocation failures silently reduce fan-out. Security socket options require either `CAP_NET_ADMIN` or `CAP_NET_RAW`; regressions here affect link-layer security policy. Namespace support is intentionally limited to `init_net`, which is a functional limitation and a test boundary.

## Test signals
Useful tests include creating raw and datagram AF_IEEE802154 sockets, verifying raw capability gating, binding by long and short addresses, sending oversized payloads to observe `-EMSGSIZE`, receiving fan-out across multiple raw/datagram sockets, checking `WPAN_WANTLQI` control messages, testing security option permission failures, and loading/unloading the module to confirm protocol and packet handler registration unwind cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/sysfs.c -->
# sources/distributed-fs/ceph-client/net/ieee802154/sysfs.c

## Purpose
`sysfs.c` defines the sysfs device class for IEEE 802.15.4 PHY objects. It exposes a small set of read-only PHY attributes and wires class-level lifetime and power-management callbacks into cfg802154 registered devices.

## Important APIs, types, and functions
The exported class object is `wpan_phy_class`. `wpan_phy_sysfs_init()` registers it with `class_register()`, and `wpan_phy_sysfs_exit()` unregisters it. `dev_to_rdev()` maps a `struct device` back to `struct cfg802154_registered_device`. Attribute helpers define read-only `index` and `name` sysfs files. `wpan_phy_release()` frees devices through `cfg802154_dev_free()`. Under `CONFIG_PM_SLEEP`, `wpan_phy_suspend()` and `wpan_phy_resume()` delegate to `rdev_suspend()` and `rdev_resume()`.

## Control flow
Class registration installs the class name `ieee802154`, the release callback, the `pmib` attribute group, and optional PM ops. Sysfs reads resolve the class device to `cfg802154_registered_device` and format the PHY index or device name. Suspend/resume callbacks check whether the driver implements the relevant cfg802154 op, take RTNL, call the rdev wrapper, and release RTNL.

## State and persistence
The file does not create durable state. It exposes live kernel state from `wpan_phy_idx` and `wpan_phy.dev`, and class registration persists only until subsystem exit. Device memory is released when the class device refcount reaches zero.

## Dependencies and integration points
It depends on Linux driver core classes, sysfs device attributes, cfg802154 registered-device layout, RTNL locking, and cfg802154 rdev operation wrappers. It is included by the IEEE802154 core initialization path that creates and tears down PHY support.

## Risks and invariants
`dev_to_rdev()` relies on `wpan_phy.dev` being embedded in `cfg802154_registered_device`; layout changes must update the helper. PM callbacks must run under RTNL because cfg802154 device state and network devices may be touched by driver callbacks. Attribute formatting uses `sprintf()` into sysfs-provided buffers and assumes values are small.

## Test signals
Boot or module-load tests should show an `ieee802154` class. Registering a WPAN PHY should create `index` and `name` attributes with expected values. Suspend/resume tests should verify rdev callbacks are called under RTNL and that absent callbacks return success. Device teardown should free the registered device without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/sysfs.h -->
# sources/distributed-fs/ceph-client/net/ieee802154/sysfs.h

## Purpose
`sysfs.h` is the small public header for the IEEE 802.15.4 sysfs class implementation.

## Important APIs, types, and functions
It declares `wpan_phy_sysfs_init()`, `wpan_phy_sysfs_exit()`, and the external `wpan_phy_class` object.

## Control flow
There is no executable control flow in the header. Callers use the declarations to register the class during subsystem initialization and unregister it during teardown.

## State and persistence
The header owns no state. It exposes access to the class object defined in `sysfs.c`.

## Dependencies and integration points
The include guard `__IEEE802154_SYSFS_H` protects repeated inclusion. Integration is with the local IEEE802154 core and any code that needs the driver-core class for WPAN PHY devices.

## Risks and invariants
The main invariant is that the function declarations and the class object stay in sync with `sysfs.c`. Because `wpan_phy_class` is a `const struct class`, consumers should not mutate it.

## Test signals
Compilation is the primary signal. Link failures would reveal declaration/definition drift; init/exit tests for `sysfs.c` indirectly validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/trace.c -->
# sources/distributed-fs/ceph-client/net/ieee802154/trace.c

## Purpose
`trace.c` instantiates the cfg802154 tracepoints declared in `trace.h`.

## Important APIs, types, and functions
The file defines `CREATE_TRACE_POINTS` before including `trace.h`, guarded by `#ifndef __CHECKER__`. It includes `<linux/module.h>` for module context.

## Control flow
There is no runtime control flow beyond tracepoint registration generated by the tracepoint macros at build/module load time.

## State and persistence
Tracepoint state is generated by the kernel tracing framework. The file itself owns no mutable data.

## Dependencies and integration points
It depends on `trace.h` and the Linux tracepoint generation mechanism. The `__CHECKER__` guard avoids sparse/checker processing problems with tracepoint instantiation.

## Risks and invariants
Exactly one C file should define `CREATE_TRACE_POINTS` for the trace header; duplicating it would create duplicate definitions. Omitting this file would leave trace declarations without generated tracepoint storage.

## Test signals
Build and link tests validate tracepoint instantiation. Runtime tracing tests can enable cfg802154 events under tracefs and confirm events appear when rdev operation wrappers execute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/trace.h -->
# sources/distributed-fs/ceph-client/net/ieee802154/trace.h

## Purpose
`trace.h` declares tracepoints for cfg802154 registered-device operations. It makes WPAN PHY, WPAN device, channel, CCA, scan, beacon, association, and return-value events observable through the Linux tracing subsystem.

## Important APIs, types, and functions
The header sets `TRACE_SYSTEM cfg802154`, defines helper macros such as `WPAN_PHY_ENTRY`, `WPAN_DEV_ENTRY`, `WPAN_CCA_ENTRY`, and `BOOL_TO_STR`, then uses `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `DEFINE_EVENT_PRINT`, and `TRACE_EVENT`. Events include `802154_rdev_suspend`, `802154_rdev_resume`, `802154_rdev_add_virtual_intf`, `802154_rdev_del_virtual_intf`, channel and TX power setters, CCA setters, PAN ID and short address setters, CSMA/backoff/retry/LBT/ack defaults, scan and beacon operations, association/disassociation, and `802154_rdev_return_int`.

## Control flow
The tracepoint macros generate event classes and per-event record/print callbacks. At runtime, cfg802154 rdev wrapper code calls the generated trace hooks when operations are attempted or return. Each event copies stable values into `__entry` fields during `TP_fast_assign()` and formats them through `TP_printk()`.

## State and persistence
The header does not manage subsystem state. Trace records are transient ring-buffer entries controlled by the tracing subsystem. Event payloads intentionally copy names and identifiers so traces do not depend on later object lifetime.

## Dependencies and integration points
It includes `<linux/tracepoint.h>` and `<net/cfg802154.h>`. `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` integrate with kernel trace generation, while `trace.c` supplies the single `CREATE_TRACE_POINTS` translation unit.

## Risks and invariants
Tracepoint prototypes must match the wrapper call sites and the underlying cfg802154 types. Event names beginning with digits are accepted by the trace macro conventions but should remain consistent for userspace tooling. `WPAN_DEV_ASSIGN` handles null or error `wpan_dev` pointers by recording identifier zero; consumers should treat zero as a sentinel.

## Test signals
Build coverage catches mismatched prototypes. Runtime signals include enabling cfg802154 trace events, invoking nl802154 operations such as virtual-interface creation or channel changes, and verifying printed fields match the requested PHY/device/action.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ife/Kconfig -->
# sources/distributed-fs/ceph-client/net/ife/Kconfig

## Purpose
`net/ife/Kconfig` adds the configuration switch for Inter-FE encapsulation support.

## Important APIs, types, and functions
The single symbol is `NET_IFE`, a tristate `menuconfig` titled `Inter-FE based on IETF ForCES InterFE LFB`, defaulting to `n`.

## Control flow
Kconfig selection controls whether `ife.o` is built in, built as a module, or omitted. Choosing module mode names the module `ife`.

## State and persistence
The persistent result is the generated kernel configuration value for `CONFIG_NET_IFE`; no runtime state is represented here.

## Dependencies and integration points
The symbol is consumed by `net/ife/Makefile`. The help text points to the InterFE LFB design and the traffic-control classifier/action distribution use case.

## Risks and invariants
Because the symbol has no explicit dependencies, the implementation must compile wherever the surrounding networking stack supports it. Changing the symbol name would break Makefile wiring and downstream configs.

## Test signals
Configuration tests should verify `CONFIG_NET_IFE=y` links `ife.o`, `CONFIG_NET_IFE=m` builds `ife.ko`, and `CONFIG_NET_IFE=n` omits the object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ife/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ife/Makefile -->
# sources/distributed-fs/ceph-client/net/ife/Makefile

## Purpose
The IFE Makefile wires the Inter-FE encapsulation implementation into the kernel build.

## Important APIs, types, and functions
It contains one build rule: `obj-$(CONFIG_NET_IFE) += ife.o`.

## Control flow
Kbuild expands the rule according to `CONFIG_NET_IFE`, compiling `ife.c` into built-in networking code or a loadable module when enabled.

## State and persistence
The file owns no runtime state. Its output is build-system state in the generated object/module list.

## Dependencies and integration points
It depends on `NET_IFE` from `Kconfig` and on `ife.c` as the object source.

## Risks and invariants
The object name must match the implementation file and module name described in Kconfig. Additional source files would require updating this Makefile to avoid missing symbols.

## Test signals
Kbuild with `CONFIG_NET_IFE=y` or `m` should produce `ife.o`; disabled configs should not compile the directory object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ife/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ife/ife.c -->
# sources/distributed-fs/ceph-client/net/ife/ife.c

## Purpose
`ife.c` implements helpers for encoding and decoding Inter-FE metadata encapsulation. It manipulates skbuff layout to prepend an outer Ethernet header and IFE metadata block, then provides TLV helpers used by traffic-control actions or other IFE consumers.

## Important APIs, types, and functions
The file exports `ife_encode()`, `ife_decode()`, `ife_tlv_meta_decode()`, `ife_tlv_meta_next()`, and `ife_tlv_meta_encode()`. Internal wire structs are `struct ifeheadr` for total metadata length and `struct meta_tlvhdr` for per-metadata TLVs.

## Control flow
`ife_encode()` ensures enough headroom with `skb_cow_head()`, snapshots the existing Ethernet header, pushes space for outer header plus IFE metadata header, copies the original Ethernet header to the new front, resets the MAC header, writes total metadata length, and returns a pointer to TLV data. `ife_decode()` validates enough linear data, reads the metadata length after the hard header, validates length, pulls the hard header plus IFE metadata from the skb, updates the MAC header, stores metadata payload length, and returns the TLV data pointer. TLV decoding first runs `__ife_tlv_meta_valid()` to verify header presence, minimum netlink-attribute length, alignment overflow, and end bounds; encoding writes type/length in network order, zeros aligned padding, and copies the value.

## State and persistence
All state is carried in the skb data buffer. The helpers do not keep global or per-net state and do not persist metadata outside packet memory.

## Dependencies and integration points
The implementation depends on skbuff headroom/pull helpers, netdevice hard-header length, Ethernet headers, netlink attribute alignment (`NLA_HDRLEN`, `NLA_ALIGN`, `nla_total_size()`), and the public `<net/ife.h>` constants such as `IFE_METAHDRLEN`.

## Risks and invariants
The caller must provide coherent `metalen` values and enough skb context, including `skb->dev`. Decode returns a pointer into skb data after mutating the skb with `__skb_pull()`, so callers must consume metadata before further modifications invalidate it. TLV helpers rely on network byte order and reject malformed or overflowing lengths; bypassing them risks out-of-bounds reads.

## Test signals
Tests should round-trip an skb through encode/decode, verify hard header preservation, validate metadata length accounting, exercise malformed TLVs with short lengths and overlong aligned lengths, and confirm exported helpers work for multiple TLVs using `ife_tlv_meta_next()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ife/ife.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/Kconfig -->
# sources/distributed-fs/ceph-client/net/ipv4/Kconfig

## Purpose
`net/ipv4/Kconfig` defines build-time feature selection for the IPv4 networking stack, including multicast/routing, tunnels, IPsec transforms, diagnostics, TCP congestion control algorithms, and TCP authentication/signature support.

## Important APIs, types, and functions
Major symbols include `IP_MULTICAST`, `IP_ADVANCED_ROUTER`, `IP_MULTIPLE_TABLES`, `IP_ROUTE_MULTIPATH`, `IP_PNP` and its DHCP/BOOTP/RARP suboptions, `NET_IPIP`, `NET_IPGRE_DEMUX`, `NET_IP_TUNNEL`, `NET_IPGRE`, `IP_MROUTE`, `SYN_COOKIES`, `NET_IPVTI`, `NET_UDP_TUNNEL`, `NET_FOU`, `INET_AH`, `INET_ESP`, `INET_ESP_OFFLOAD`, `INET_ESPINTCP`, `INET_IPCOMP`, `INET_DIAG` and protocol-specific diag symbols, `TCP_CONG_ADVANCED` with many congestion-control algorithms, `DEFAULT_TCP_CONG`, `TCP_AO`, and `TCP_MD5SIG`.

## Control flow
Kconfig dependency and selection rules determine which source files are compiled by `net/ipv4/Makefile` and which runtime features exist. The congestion-control section either presents an advanced menu with multiple algorithms and a default-choice block, or defaults to CUBIC when advanced selection is disabled. IPsec and tunnel symbols select shared XFRM/tunnel support needed by their implementations.

## State and persistence
The durable output is `.config` state and generated `CONFIG_*` macros. Runtime defaults such as selected TCP congestion control are derived from these values but are not stored here directly.

## Dependencies and integration points
The file integrates with the IPv4 Makefile, crypto/XFRM subsystems, FIB rules, proc/sysctl features, socket diagnostic tooling, tunnel drivers, TCP congestion-control modules, and documentation referenced by help text.

## Risks and invariants
Dependency drift can create build failures or unusable configs, especially around IPsec symbols that require XFRM/crypto support and BPF TCP congestion control that is additionally gated by the Makefile on `CONFIG_BPF_JIT`. Duplicate `TCP_CONG_CUBIC` definitions intentionally cover advanced and non-advanced modes; changes must preserve default selection semantics. Security-sensitive options such as SYN cookies, TCP-AO, and TCP-MD5 have operational tradeoffs that are documented in help text.

## Test signals
Useful signals include `allnoconfig`, `defconfig`, and targeted configs for IPsec, tunnels, diagnostics, and each congestion-control algorithm. Verify `DEFAULT_TCP_CONG` strings match selected choices and that Kconfig dependencies pull required support without unexpected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/Makefile -->
# sources/distributed-fs/ceph-client/net/ipv4/Makefile

## Purpose
The IPv4 Makefile maps core IPv4 stack components and optional features to kbuild objects.

## Important APIs, types, and functions
The `obj-y` list builds core routing, protocol, TCP, UDP, ARP, ICMP, device address, FIB, fragmentation, ping, tunnel-core, offload, metrics, netlink, nexthop, and stub objects. Optional `obj-$(CONFIG_...)` entries cover tunnels, sysctl/proc, FIB rules, multicast routing, IPsec transforms, netfilter, INET diagnostics, raw/UDP/TCP diag modules, congestion-control modules, TCP signature pool, BPF UDP/TCP pieces, NetLabel CIPSO, XFRM IPv4 support, and TCP-AO.

## Control flow
Kbuild evaluates the object lists from the generated config. Composite objects are defined for GRE (`gre-y`), FOU (`fou-y`), and UDP tunnel support (`udp_tunnel-y`). `bpf_tcp_ca.o` is compiled only when both `CONFIG_BPF_JIT=y` and `CONFIG_BPF_SYSCALL` are enabled.

## State and persistence
The file has no runtime state; it determines the build graph and resulting built-in objects/modules.

## Dependencies and integration points
It consumes symbols from `net/ipv4/Kconfig` and other subsystem Kconfigs such as XFRM, BPF, NETFILTER, PROC_FS, and SYSCTL. It directly wires source files like `af_inet.c`, `arp.c`, `datagram.c`, `ah4.c`, `cipso_ipv4.c`, and `bpf_tcp_ca.c` into the build when relevant.

## Risks and invariants
Core `obj-y` entries must remain complete enough for AF_INET to initialize base protocols. Optional object rules must match Kconfig dependencies; otherwise configs may expose symbols without objects or compile objects without required infrastructure. The extra Makefile gate on `CONFIG_BPF_JIT` is a subtle integration constraint for BPF TCP congestion control.

## Test signals
Build-matrix coverage should exercise minimal IPv4, proc/sysctl, netfilter, IPsec AH/ESP/IPComp, tunnels, all diagnostics, congestion-control modules, NetLabel, XFRM, and BPF JIT/SYSCALL combinations. `make V=1` or generated `.mod` files can confirm expected object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/af_inet.c -->
# sources/distributed-fs/ceph-client/net/ipv4/af_inet.c

## Purpose
`af_inet.c` is the PF_INET socket-family core for IPv4. It creates INET sockets, maps socket type/protocol pairs to protocol implementations, implements common socket operations, registers base IPv4 protocols, installs packet/offload handlers, and initializes per-network-namespace IPv4 defaults and statistics.

## Important APIs, types, and functions
Important exports include `inet_sock_destruct()`, `inet_listen()`, `inet_release()`, `inet_bind()`, `__inet_bind()`, `inet_dgram_connect()`, `__inet_stream_connect()`, `inet_stream_connect()`, `__inet_accept()`, `inet_accept()`, `inet_getname()`, `inet_send_prepare()`, `inet_sendmsg()`, `inet_splice_eof()`, `inet_recvmsg()`, `inet_shutdown()`, `inet_ioctl()`, `inet_stream_ops`, `inet_dgram_ops`, `inet_register_protosw()`, `inet_unregister_protosw()`, `inet_sk_rebuild_header()`, `inet_sk_set_state()`, `inet_gso_segment()`, `inet_gro_receive()`, `inet_current_timestamp()`, `inet_recv_error()`, `inet_gro_complete()`, `inet_ctl_sock_create()`, and SNMP fold helpers. Internal registries include `inetsw[]`, `inetsw_array[]`, `inet_family_ops`, `ip_packet_type`, and `ipip_offload`.

## Control flow
`inet_create()` looks up the requested socket type/protocol in `inetsw`, tries module autoload on misses, checks raw-socket capability, allocates the protocol socket, initializes default IPv4 fields, hashes protocol-number sockets, runs protocol init, and invokes cgroup BPF socket hooks. Bind and connect paths apply cgroup BPF hooks, address validity checks, privileged-port checks, port allocation, route lookup, autobind, nonblocking stream-connect waits, and disconnect semantics. Send/receive wrappers perform autobind/RPS bookkeeping and indirectly call TCP or UDP fast paths. `inet_init()` registers TCP/UDP/raw/ping protos, registers PF_INET, installs base `net_protocol` handlers for ICMP/UDP/TCP/IGMP, populates `inetsw`, initializes ARP/IP/TCP/UDP/raw/ping/ICMP/mroute/pernet/proc/fragmentation/tunnel subsystems, and adds the IPv4 packet handler. `ipv4_offload_init()` separately registers GSO/GRO offloads.

## State and persistence
Global state includes the `inetsw` protocol-switch lists and packet/offload registrations. Per-socket state lives in `struct inet_sock`, route caches, socket state, multicast membership, IP options, and cgroup/BPF-controlled settings. Per-net state includes IPv4 sysctl defaults, local port ranges, ping group ranges, and per-cpu MIB allocations. All state is runtime kernel state, not durable storage.

## Dependencies and integration points
The file integrates with TCP, UDP, raw, ping, ICMP, ARP, FIB/routing, IP input, fragmentation, multicast, procfs, sysctl, XFRM, BPF cgroup hooks, MPTCP stats, GRO/GSO offload, packet handlers, net namespaces, l3mdev, netfilter includes, and PSP socket association cleanup. User-visible integration is the AF_INET socket API and legacy ioctls for routes, ARP, and interface IPv4 addresses.

## Risks and invariants
The `inetsw` list ordering prevents non-permanent protocols from overriding permanent core protocols; registration changes must preserve this. Socket state transitions in stream connect, shutdown, and accept have subtle blocking and race semantics. `inet_sock_destruct()` warns on alive or non-closed stream sockets and must free IP options and dst references exactly once. Initialization order is critical: base protocols and packet handlers depend on prior proto and subsystem registration. GSO/GRO code assumes validated IPv4 headers without options for aggregation and must update IDs, lengths, checksums, and encapsulation headers correctly.

## Test signals
Signals include IPv4 TCP/UDP/raw/ping socket creation and module autoload behavior, raw capability failures, bind to local/nonlocal/multicast/broadcast addresses, cgroup BPF bind/connect hooks, blocking and nonblocking TCP connect including Fast Open, route/ARP/interface ioctls, protocol registration/unregistration for modules, network namespace creation defaults, `/proc/net` IPv4 entries, SNMP counters, packet receive through `ip_rcv`, and GSO/GRO segmentation/completion for TCP/UDP/IPIP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/af_inet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ah4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/ah4.c

## Purpose
`ah4.c` implements the IPv4 IPsec Authentication Header transform for XFRM. It authenticates immutable IPv4 header fields and payload, handles extended sequence numbers, registers AH as an IPv4 XFRM type/protocol, and processes ICMP errors relevant to AH state.

## Important APIs, types, and functions
Key internal helpers include `ah_alloc_tmp()`, `ah_tmp_auth()`, `ah_tmp_icv()`, `ah_tmp_req()`, `ah_req_sg()`, and `ip_clear_mutable_options()`. Transform entry points are `ah_output()`, `ah_output_done()`, `ah_input()`, `ah_input_done()`, `ah4_err()`, `ah_init_state()`, `ah_destroy()`, and `ah4_rcv_cb()`. Registration objects are `ah_type` and `ah4_protocol`, installed by `ah4_init()` and removed by `ah4_fini()`.

## Control flow
Outbound processing makes skb data writable, pushes to the network header, saves mutable header fields/options, clears fields excluded from AH ICV, fills AH header fields including SPI and sequence number, optionally appends ESN high bits to the scatterlist, computes the ahash digest, writes the truncated ICV, restores header fields, and resumes XFRM output. Inbound processing validates AH header length against full or truncated ICV size, unshares the skb, copies the original IP header and received auth data into temporary storage, clears mutable fields, includes ESN high bits when configured, computes and compares the ICV with `crypto_memneq()`, removes the AH header, restores the IP header, updates transport header placement, and returns the next header. Async crypto completions mirror the synchronous completion steps and resume XFRM input/output.

## State and persistence
Per-XFRM-state AH data is stored in `struct ah_data` attached to `x->data`, including the crypto ahash handle and ICV lengths. Temporary per-packet state is stored in `AH_SKB_CB(skb)->tmp`. No persistent storage exists beyond runtime XFRM state.

## Dependencies and integration points
The file depends on the crypto ahash API, XFRM state/type/protocol registration, IPv4 header and options helpers, scatterlist conversion from skbs, ICMP PMTU/redirect handling, PF_KEY algorithm descriptions, and module aliasing for `XFRM_PROTO_AH`.

## Risks and invariants
AH requires an auth algorithm and rejects encapsulation. Mutable IPv4 options must be zeroed exactly as AH expects while immutable options remain covered; mistakes break interoperability or authentication. Header length and alignment differ for `XFRM_STATE_ALIGN4` and default align8 modes. Temporary storage allocation uses `GFP_ATOMIC`, so packet processing can fail under pressure. ESN high bits must be hashed in the correct byte order and position.

## Test signals
Tests should create IPv4 AH XFRM states with supported auth algorithms, verify outbound AH packets and inbound validation, exercise truncated/full ICV lengths, tunnel and transport modes, ESN, IPv4 options including source route/CIPSO/router alert, async crypto completion, ICMP fragmentation-needed PMTU updates, redirect handling, and module load/unload registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/ah4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/arp.c -->
# sources/distributed-fs/ceph-client/net/ipv4/arp.c

## Purpose
`arp.c` implements IPv4 Address Resolution Protocol support. It owns the ARP neighbor table, packet generation and receive processing, proxy/gratuitous ARP policy, user ioctl management, `/proc/net/arp` output, and device-event reactions.

## Important APIs, types, and functions
The central exported table is `arp_tbl`; exported helpers include `arp_send()`, `arp_create()`, `arp_xmit()`, `arp_invalidate()`, `arp_ioctl()`, `arp_ifdown()`, and `arp_init()`. Neighbor callbacks include `arp_hash()`, `arp_key_eq()`, `arp_constructor()`, `arp_solicit()`, `arp_error_report()`, `parp_redo()`, and `arp_is_multicast()`. Packet paths include `arp_rcv()` and `arp_process()`. Policy helpers include `arp_ignore()`, `arp_accept()`, `arp_filter()`, `arp_fwd_proxy()`, `arp_fwd_pvlan()`, and `arp_is_garp()`.

## Control flow
`arp_init()` initializes the neighbor table, registers the ARP packet handler, creates per-net proc entries, registers neighbor sysctls when enabled, and installs a netdevice notifier. Outbound solicitation is driven by neighbor core through `arp_solicit()`, which chooses a source address according to `arp_announce`, decides unicast/app/broadcast probing, and sends an ARP request. `arp_create()` builds hardware and protocol headers for device-specific ARP formats; `arp_xmit()` sends through the ARP netfilter output hook. Inbound `arp_rcv()` filters no-ARP/otherhost/loopback packets, validates header size and address lengths, clears neighbor control data, and passes through the ARP netfilter input hook to `arp_process()`. `arp_process()` validates hardware/protocol combinations, drops invalid targets, handles duplicate-address-detection requests, replies for local addresses or proxy cases, queues delayed proxy replies when configured, and updates neighbor entries for replies, requests, and accepted gratuitous ARP.

## State and persistence
Runtime state lives in `arp_tbl`, neighbor entries, proxy-neighbor entries, per-device IPv4 config, proc entries, and netdevice notifier registration. ioctl operations can create permanent neighbor entries or proxy settings, but these remain kernel runtime state unless userspace persists them externally.

## Dependencies and integration points
The file integrates with generic neighbor infrastructure, IPv4 routing and address-type lookups, inet device configuration, netfilter ARP hooks, netdevice events, procfs seq_file, sysctl neighbor parameters, AX.25/NETROM/FDDI/FireWire/Infiniband/IPGRE hardware variants, tunnel metadata replies, and AF_INET ioctls via `inet_ioctl()`.

## Risks and invariants
ARP reply policy is controlled by many sysctls (`arp_ignore`, `arp_accept`, `arp_filter`, proxy ARP, PVLAN, drop gratuitous ARP), so regressions can create spoofing exposure or connectivity failures. Neighbor locking and RCU contexts must be respected when updating entries. `arp_process()` intentionally treats DAD, GARP, proxy ARP, and local replies differently; merging cases can break standards behavior. Device address changes and carrier loss must flush or invalidate affected neighbor state to avoid stale L2 addresses.

## Test signals
Test ARP request/reply exchange on Ethernet and no-ARP devices, multicast mapping, neighbor solicitation retries, proxy ARP and PVLAN behavior, DAD requests with sender IP zero, gratuitous ARP accept/drop settings, ARP netfilter hooks, `SIOCSARP`/`SIOCGARP`/`SIOCDARP` permission and behavior, `/proc/net/arp` output, device address changes, carrier down eviction, and namespace-specific proc entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/arp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/bpf_tcp_ca.c -->
# sources/distributed-fs/ceph-client/net/ipv4/bpf_tcp_ca.c

## Purpose
`bpf_tcp_ca.c` enables BPF `struct_ops` programs to implement TCP congestion-control algorithms through the kernel `tcp_congestion_ops` interface.

## Important APIs, types, and functions
The central registration object is `bpf_tcp_congestion_ops`, backed by verifier ops `bpf_tcp_ca_verifier_ops` and CFI stubs in `__bpf_ops_tcp_congestion_ops`. Initialization discovers BTF IDs in `bpf_tcp_ca_init()`. Verifier helpers are `bpf_tcp_ca_is_valid_access()`, `bpf_tcp_ca_btf_struct_access()`, and `bpf_tcp_ca_get_func_proto()`. Struct-ops lifecycle hooks are `bpf_tcp_ca_init_member()`, `bpf_tcp_ca_reg()`, `bpf_tcp_ca_unreg()`, `bpf_tcp_ca_update()`, and `bpf_tcp_ca_validate()`. `bpf_tcp_ca_kfunc_set` exposes selected Reno/congestion helpers as kfuncs. `bpf_tcp_ca_kfunc_init()` registers kfuncs and struct_ops at late init.

## Control flow
During init, the file resolves BTF types for `sock`, `tcp_sock`, and `tcp_congestion_ops`. The verifier promotes safe `struct sock *` BTF context pointers to `tcp_sock *`, limits write access to selected pacing, congestion-window, ECN, app-limited, ACK pending, and CA-private fields, and exposes a constrained helper set. BPF object initialization copies only valid congestion-control flags and a valid BPF object name. Register/update/unregister operations delegate to TCP congestion-control core functions. Runtime callbacks are dispatched through BPF struct_ops, with C stubs present for CFI-compatible function pointers.

## State and persistence
Global runtime state stores BTF type pointers and IDs plus the registered BPF struct_ops descriptor. Individual BPF congestion controls are registered in TCP core state through BPF links; persistence is only as long as the BPF object/link and kernel runtime.

## Dependencies and integration points
The file depends on BPF verifier infrastructure, BTF, BPF struct_ops, BPF socket storage helpers, TCP congestion-control registration, TCP helper kfuncs, and the Makefile condition requiring BPF JIT plus BPF syscall support.

## Risks and invariants
Verifier access restrictions are security-critical because BPF programs receive live TCP socket pointers. `setsockopt()` and `getsockopt()` are intentionally unavailable from `release()` callbacks to prevent resource allocation or surprising side effects during teardown. Field offsets are BTF-driven; struct layout changes must keep allowed writes intentional. TCP core validation remains the final gate before registration.

## Test signals
Selftests should load BPF TCP congestion-control struct_ops, verify registration/update/unregistration, exercise allowed and denied field writes, confirm `sock` pointer promotion to `tcp_sock`, call exposed kfuncs, test helper availability differences for `release()`, use BPF sk storage, and run traffic to confirm callbacks affect congestion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/bpf_tcp_ca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/cipso_ipv4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/cipso_ipv4.c

## Purpose
`cipso_ipv4.c` implements CIPSO v4 label handling for NetLabel and IPv4. It manages DOI definitions, caches parsed label mappings, validates CIPSO IP options, translates between on-wire CIPSO tags and local LSM security attributes, and adds/removes CIPSO options on sockets, request sockets, and skbs.

## Important APIs, types, and functions
Global controls include `cipso_v4_cache_enabled`, `cipso_v4_cache_bucketsize`, `cipso_v4_rbm_optfmt`, and `cipso_v4_rbm_strictvalid`. DOI APIs include `cipso_v4_doi_add()`, `cipso_v4_doi_remove()`, `cipso_v4_doi_getdef()`, `cipso_v4_doi_putdef()`, `cipso_v4_doi_walk()`, and `cipso_v4_doi_free()`. Cache APIs include `cipso_v4_cache_invalidate()` and `cipso_v4_cache_add()`. Packet/socket APIs include `cipso_v4_optptr()`, `cipso_v4_validate()`, `cipso_v4_error()`, `cipso_v4_sock_setattr()`, `cipso_v4_req_setattr()`, `cipso_v4_sock_delattr()`, `cipso_v4_req_delattr()`, `cipso_v4_getattr()`, `cipso_v4_sock_getattr()`, `cipso_v4_skbuff_setattr()`, and `cipso_v4_skbuff_delattr()`.

## Control flow
Initialization allocates the fixed bucket array for the mapping cache. DOI add validates DOI/tag/type compatibility, sets a refcount, inserts the DOI under a spinlock with RCU list semantics, and audits the result. DOI removal deletes from the RCU list, drops a reference, invalidates the cache when the last reference is released, and frees with `call_rcu()`. Option generation tries the DOI's configured tags in order, maps MLS level/categories from host to network, emits one supported tag, and writes the CIPSO option header. Option parsing first checks the cache, then looks up the DOI and dispatches by tag type to reconstruct NetLabel security attributes. Validation walks all tags in an option, checks DOI and tag membership, enforces tag lengths and mapping validity, and rejects local tags unless the skb is loopback. Socket/request setters allocate new `ip_options_rcu`, install a generated option, and update TCP extended-header length/MSS for established INET connection sockets. Skb setters may grow or shrink the IPv4 header, overwrite options to guarantee label placement, update `IPCB(skb)->opt`, total length, IHL, and checksum.

## State and persistence
DOI definitions live in the RCU-protected `cipso_v4_doi_list` with refcounts and audit-visible add/remove events. The mapping cache is a fixed hash table of bucket lists protected by per-bucket spinlocks; entries reference `netlbl_lsm_cache` objects. Socket labels persist in `inet_opt` or request-sock options until explicitly removed or the socket/request is freed. Packet labels persist only in skb data.

## Dependencies and integration points
The file integrates with IPv4 options, ICMP errors, NetLabel/LSM security attributes, audit logging, RCU, spinlocks, jhash, skb copy-on-write, TCP MSS recalculation through `inet_connection_sock`, request sockets, and unaligned network-byte-order helpers. It is built when `CONFIG_NETLABEL` enables CIPSO support in the IPv4 Makefile.

## Risks and invariants
CIPSO option length is capped by the 40-byte IPv4 option space; generation must fail rather than emit truncated security labels. The implementation assumes one MAC tag per option in parsing/generation, matching supported use but limiting future multi-tag behavior. DOI lifetime and cache references must stay synchronized to avoid use-after-free; cache invalidation on DOI release is critical. `cipso_v4_skbuff_setattr()` overwrites existing options by design, which can affect packets carrying other IPv4 options. Strict validation of restricted bitmap tags is sysctl-controlled and has interoperability/security tradeoffs.

## Test signals
Tests should cover DOI add/remove/walk for pass, trans, and local mappings; invalid tag/type combinations; cache hit/miss/add/invalidate behavior; validation errors with correct offending option offsets; RBM/ENUM/RANGE/LOCAL tag generation and parsing; socket/request set/get/delete paths including TCP MSS updates; skb set/delete with header growth and shrink; loopback-only local tags; ICMP administrative-prohibited errors; and NetLabel integration with LSM secattr cache references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/cipso_ipv4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/datagram.c -->
# sources/distributed-fs/ceph-client/net/ipv4/datagram.c

## Purpose
`datagram.c` contains common IPv4 datagram socket connect and route-cache refresh logic used by UDP and raw-style datagram protocols.

## Important APIs, types, and functions
It exports `__ip4_datagram_connect()`, `ip4_datagram_connect()`, and `ip4_datagram_release_cb()`.

## Control flow
`__ip4_datagram_connect()` validates a `sockaddr_in`, resets the cached dst, chooses an output interface and source address from bound-device, multicast, or unicast socket settings, performs `ip_route_connect()`, rejects broadcast routes unless `SOCK_BROADCAST` is enabled, updates destination/source address and port fields, rehashes if the receive source address becomes known, marks reuseport sockets as connected, sets `TCP_ESTABLISHED`, picks a transmit hash, randomizes the IP ID base, and installs the route dst. `ip4_datagram_connect()` wraps that sequence with socket locking. `ip4_datagram_release_cb()` runs when releasing the socket lock; if the cached dst is obsolete and fails validation, it builds a flow from current inet state, performs a new route lookup, and updates the socket dst cache with `sk_dst_set()`.

## State and persistence
State changes are per-socket: `inet_daddr`, `inet_dport`, `inet_saddr`, `inet_rcv_saddr`, `inet_id`, `sk_state`, transmit hash, reuseport connected flag, and `sk_dst_cache`. There is no durable persistence.

## Dependencies and integration points
The file depends on IPv4 route lookup, multicast socket fields, l3 master detection, socket reuseport state, dst cache APIs, TCP state constants reused for datagram connected state, and IP statistics for `OUTNOROUTES`.

## Risks and invariants
Broadcast connect must remain gated by `SOCK_BROADCAST`. Rehashing after `inet_rcv_saddr` is assigned is required for socket lookup correctness. The release callback deliberately uses `sk_dst_set()` despite holding the socket lock because UDP transmit paths can manipulate the dst cache locklessly. Route errors must not leave partially connected socket state.

## Test signals
Tests should connect UDP sockets to unicast, multicast, broadcast with and without `SO_BROADCAST`, bound-device and multicast-interface cases, unreachable routes with IP stats increments, reuseport connected behavior, source address selection, socket rehash on first receive address assignment, and route-cache refresh after device or route changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/datagram.c -->
