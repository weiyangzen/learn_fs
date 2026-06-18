# Research: subset-b-005448

Grouped research for the IPWireless PCMCIA tty/PPP driver pieces and three tty multiport/debug-channel drivers. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/main.c -->
# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/main.c

## Purpose
`main.c` is the PCMCIA-facing entry point for the IPWireless 3G card driver. It matches supported cards, allocates the per-device `ipw_dev`, configures I/O and memory windows, wires the hardware, network, and tty layers together, registers the interrupt handler, and tears everything down on remove.

## Important APIs, Types, And Functions
- `ipw_ids` matches manufacturer/card IDs `0x02f2:0x0100` and `0x02f2:0x0200`.
- Module parameters `debug`, `loopback`, and `out_queue` control verbose logging, raw RAS tty visibility, and PPP hardware queue depth.
- `ipwireless_probe` is the `pcmcia_loop_config` callback that requests I/O space, common memory, attribute memory, maps both windows, and detects V2/V3 cards by common-memory window size.
- `config_ipwireless` sets PCMCIA config flags, initializes reboot work, initializes hardware, requests IRQs, creates network and tty contexts, performs V2/V3 hardware initialization, and enables the device last.
- `ipwireless_attach` allocates `struct ipw_dev` and hardware state, then calls configuration.
- `ipwireless_detach` and `release_ipwireless` release resources and free tty, network, hardware, and device state.
- `init_ipwireless`/`exit_ipwireless` register and unregister the tty driver and PCMCIA driver.

## Control Flow And State
Module load initializes the IPWireless tty driver first, then registers the PCMCIA driver. A matching card invokes `ipwireless_attach`, which stores `ipw_dev` in `link->priv`, creates the hardware context, and calls `config_ipwireless`. Configuration loops through PCMCIA tuples via `pcmcia_loop_config`, maps device windows, initializes hardware with common/attribute memory pointers and a reboot callback, requests IRQs, creates the PPP/network layer, creates tty devices, performs second-stage hardware setup, and finally calls `pcmcia_enable_device`.

The reboot path is asynchronous: hardware can invoke `signalled_reboot_callback`, which schedules `work_reboot`; the worker calls `pcmcia_reset_card` in process context. Removal reverses setup: device resources are disabled, tty devices are freed before network, then hardware is freed.

## State And Persistence Behavior
Runtime state is in `struct ipw_dev`: PCMCIA link, V2/V3 detection, mapped attribute/common memory, hardware/network/tty pointers, and reboot work. Hardware mappings and requested regions persist only while the card is configured. Module parameters are global and affect all instances. No on-disk state is written.

## Dependencies And Integration Points
This file depends on Linux PCMCIA services, kernel I/O mapping/resource APIs, workqueues, and the local `hardware.h`, `network.h`, `main.h`, and `tty.h` contracts. It integrates the PCMCIA device lifecycle with the local hardware interrupt handler `ipwireless_interrupt`, network creation `ipwireless_network_create`, and tty creation `ipwireless_tty_create`.

## Risks And Edge Cases
The `config_ipwireless` error path returns `-1` rather than preserving the original failure code for several post-probe failures. Partial failures after network or tty creation rely on the later detach path to free subordinate objects. The code assumes `resource[2]` and `resource[3]` are usable PCMCIA windows. Ordering matters: enabling the PCMCIA device before network/tty setup could expose interrupts too early, so the current last-step enable is intentional.

## Test Signals
Useful signals include successful module load/unload, probe/remove under PCMCIA card insertion, correct `/proc/iomem`/resource cleanup after failures, `ttyIPWp*` devices appearing for each card, PPP channel availability after opening the modem tty, IRQ delivery through the hardware layer, and reboot callback causing a card reset without running reset directly in interrupt context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/main.h -->
# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/main.h

## Purpose
`main.h` defines the shared top-level IPWireless driver identity, queue sizing constants, module parameter declarations, and `struct ipw_dev`, the object that connects PCMCIA resources with the hardware, network, and tty sublayers.

## Important APIs, Types, And Functions
- `IPWIRELESS_PCCARD_NAME`, `IPWIRELESS_PCMCIA_VERSION`, and `IPWIRELESS_PCMCIA_AUTHOR` provide module/device identity strings.
- `IPWIRELESS_TX_QUEUE_SIZE` and `IPWIRELESS_RX_QUEUE_SIZE` define 256 KiB queue sizing constants used by tty/hardware paths.
- `IPWIRELESS_STATE_DEBUG` enables local debug-state compilation paths in related code.
- `struct ipw_dev` stores `struct pcmcia_device *link`, `is_v2_card`, mapped `attr_memory` and `common_memory`, and pointers to `ipw_hardware`, `ipw_network`, and `ipw_tty`.
- `work_reboot` stores process-context work for card reset after firmware-signalled reboot.
- Externs expose global module parameters `ipwireless_debug`, `ipwireless_loopback`, and `ipwireless_out_queue`.

## Control Flow And State
This header has no executable control flow. It defines the state that `main.c` allocates and that subordinate layers indirectly depend on through pointers passed during creation. The reboot work item is initialized in `config_ipwireless` and scheduled by hardware callbacks.

## State And Persistence Behavior
The state is per-card and lives for the PCMCIA device lifetime. Memory window pointers are I/O mappings and must be unmapped during detach. The module parameter variables are process-global kernel module state and affect behavior such as debug logging and raw channel exposure.

## Dependencies And Integration Points
It includes Linux scheduling/types and PCMCIA CIS/device-service headers, and it includes `hardware.h` for hardware declarations. The structure is consumed primarily by `main.c`; its forward declarations avoid exposing concrete network and tty definitions to all users.

## Risks And Edge Cases
Because `struct ipw_dev` owns multiple independently allocated subobjects and mapped resources, cleanup must follow initialization ordering carefully. The global queue constants and module parameters are compile-time/global knobs, not per-card settings. The `IPWIRELESS_STATE_DEBUG` define may enable extra code in related files and should be kept consistent with available debug state.

## Test Signals
Build coverage should verify all forward declarations and PCMCIA types resolve. Runtime validation is indirect: card probe must allocate an `ipw_dev`, mapped memory pointers must be non-NULL only after successful mapping, and detach must leave no resource leaks or stale tty/network pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/network.c -->
# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/network.c

## Purpose
`network.c` bridges IPWireless card channels to Linux `ppp_generic` and associated diagnostic ttys. It registers a PPP channel when the modem tty opens, sends outbound PPP frames to the hardware RAS channel, routes inbound RAS data either into PPP or tty devices, propagates modem-control changes, and manages PPP close/open work asynchronously.

## Important APIs, Types, And Functions
- `struct ipw_network` stores the hardware pointer, optional `ppp_channel`, associated tty matrix, queue/backpressure counters, locks, PPP ioctl state, RAS control lines, and online/offline work items.
- `ipwireless_ppp_start_xmit` adds the PPP `0xff 0x03` header, enforces `ipwireless_out_queue`, calls `ipwireless_send_packet`, and blocks/wakes PPP output when the hardware queue is full.
- `notify_packet_sent` decrements queued packet count and calls `ppp_output_wakeup` when needed.
- `ipwireless_ppp_ioctl` implements PPP async-map, flags, and MRU ioctls similar to `ppp_async_ioctl`.
- `do_go_online` allocates and registers a `ppp_channel`; `do_go_offline` unregisters it under `close_lock`.
- `ipwireless_network_packet_received` sends online modem RAS data to PPP and all other associated data to tty devices.
- `ipwireless_network_notify_control_line_change` updates cached RAS line state and notifies associated ttys.
- Lifecycle APIs are `ipwireless_network_create`, `ipwireless_network_free`, `ipwireless_ppp_open`, and `ipwireless_ppp_close`.

## Control Flow And State
Creation initializes a spinlock, close mutex, work items, stores the hardware pointer, and associates the network object with the hardware layer. Opening the modem tty schedules `work_go_online`; the worker allocates a PPP channel with `hdrlen = 2`, default MRU, and ACCM defaults, then registers it. Closing schedules `work_go_offline`, clears the channel pointer under the spinlock, and unregisters outside the lock.

Outbound PPP enters through `start_xmit`. If queued packets are below `ipwireless_out_queue`, the function reserves a queue slot, prepends or copies the two-byte PPP header, submits to hardware with a completion callback, frees the skb on success, and returns ownership accepted. If the queue is full it sets `ppp_blocked` and returns 0 so PPP retries after `notify_packet_sent` wakes it.

Inbound hardware packets are fanned out to associated ttys. If the packet is on the RAS channel, DCD is asserted, and the tty is the modem tty, the function locks out PPP close, strips an optional PPP header, creates an skb, and calls `ppp_input`. Otherwise it calls `ipwireless_tty_received`.

## State And Persistence Behavior
`ppp_channel`, `ppp_blocked`, `outgoing_packets_queued`, MRU, ACCM fields, flags, and cached RAS control lines are runtime-only state. Associated tty pointers are populated by `tty.c` and cleared during tty teardown. `shutting_down` is set during free but not otherwise used in this file. No persistent storage exists.

## Dependencies And Integration Points
The file depends on `ppp_generic`, `ppp-ioctl`, `sk_buff`, spinlocks, mutexes, workqueues, and local hardware/tty APIs. Hardware integration is through `ipwireless_send_packet`, `ipwireless_associate_network`, and `ipwireless_stop_interrupts`. TTY integration is through association APIs, modem checks, receive delivery, and control-line notifications.

## Risks And Edge Cases
On `ipwireless_send_packet` failure after incrementing `outgoing_packets_queued`, the counter is not decremented in this function, so repeated send failures can leave PPP blocked until other callbacks run. Associated tty arrays are updated without explicit locking, relying on lifecycle ordering. PPP input uses `network->ppp_channel` after dropping the spinlock but while holding `close_lock`, so close ordering is critical. The code broadcasts packets/control to up to two ttys per channel, which is intentional for modem/monitor pairing but can duplicate data paths.

## Test Signals
Exercise modem tty open/close and verify PPP channel indices/units appear and disappear. Send traffic until the hardware queue limit and confirm PPP blocks then wakes on send callbacks. Receive RAS packets with and without the `0xff 0x03` header and confirm PPP receives normalized skb data. Toggle DCD and verify traffic switches between PPP routing and tty routing. Run teardown while traffic is active to catch close/workqueue races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/network.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/network.h -->
# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/network.h

## Purpose
`network.h` declares the IPWireless network-layer interface used by the hardware and tty layers. It names card channel indices, exposes packet/control-line callbacks from hardware, and exposes PPP and tty association helpers to the tty layer.

## Important APIs, Types, And Functions
- Channel constants define `IPW_CHANNEL_RAS`, `IPW_CHANNEL_DIALLER`, `IPW_CHANNEL_CONSOLE`, and `NO_OF_IPW_CHANNELS`.
- `ipwireless_network_packet_received` and `ipwireless_network_notify_control_line_change` are hardware-to-network entry points.
- `ipwireless_network_create` and `ipwireless_network_free` manage the network object.
- `ipwireless_associate_network_tty` and `ipwireless_disassociate_network_ttys` connect tty devices to card channels.
- `ipwireless_ppp_open` and `ipwireless_ppp_close` request PPP channel registration/unregistration.
- `ipwireless_ppp_channel_index`, `ipwireless_ppp_unit_number`, and `ipwireless_ppp_mru` expose PPP metadata to tty ioctls.

## Control Flow And State
The header does not implement control flow. It defines the contract by which hardware delivers channel events to `network.c` and by which `tty.c` opens/closes PPP and queries PPP identifiers. The RAS, dialler, and console channel constants determine routing decisions in both network and tty creation.

## State And Persistence Behavior
`struct ipw_network`, `struct ipw_tty`, and `struct ipw_hardware` are opaque here. State ownership remains in the implementing modules. The channel constants are stable protocol identifiers matching firmware expectations.

## Dependencies And Integration Points
The header depends only on Linux types and local opaque structs. It integrates the local hardware receive/control callbacks with tty-visible modem and monitor devices, and with Linux PPP through wrapper APIs.

## Risks And Edge Cases
`NO_OF_IPW_CHANNELS` is 5 even though only three channel names are exposed in this header; array users must respect the full count. Callers must pass valid channel indices because the implementation indexes fixed arrays directly. PPP query functions return negative values when no PPP channel is registered, and tty ioctl callers must propagate that as device absence.

## Test Signals
Build-time signals include all hardware and tty users compiling against the opaque declarations. Runtime signals include correct routing for RAS versus dialler channels, no out-of-bounds channel access, and PPP channel metadata returning valid values only while the PPP channel is online.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/network.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/setup_protocol.h -->
# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/setup_protocol.h

## Purpose
`setup_protocol.h` defines packed wire-format messages and signal numbers for the IPWireless setup protocol exchanged with the card firmware. It covers version negotiation, channel configuration, open/close notifications, driver information, and firmware reboot acknowledgement.

## Important APIs, Types, And Functions
- `TL_SETUP_VERSION`, `TL_SETUP_VERSION_QRY_TMO`, and `TL_SETUP_MAX_VERSION_QRY` define setup protocol versioning and retry timing.
- Signal numbers include version query/response, config/config-done, open/close, info/ack, and reboot/ack messages.
- Packed structs model each message: `tl_setup_get_version_qry`, `tl_setup_get_version_rsp`, `tl_setup_config_msg`, `tl_setup_config_done_msg`, `tl_setup_open_msg`, `tl_setup_close_msg`, `tl_setup_info_msg`, `tl_setup_info_msgAck`, and `TlSetupRebootMsgAck`.
- Driver identity constants include `COMM_DRIVER`, `NDISWAN_DRIVER`, and NDISWAN version fields used in info messages.
- `union ipw_setup_rx_msg` groups receive-side message formats for parsing.

## Control Flow And State
This header has no executable control flow. Its structs are consumed by the hardware/setup implementation to serialize and parse firmware setup messages. Typical flow is version query until a matching version response, per-port configuration messages, config-done, asynchronous open/close notifications, optional info exchange, and reboot acknowledgement.

## State And Persistence Behavior
The state is protocol state in transit rather than stored kernel state. All structs are packed and byte-sized, so their layout is persistent across host/compiler boundaries and must match firmware exactly.

## Dependencies And Integration Points
The header is protocol glue between Linux driver code and IPWireless firmware. It integrates with the hardware layer that frames setup packets and with higher layers that need channel open/close and reboot events reflected as tty/PPP state changes.

## Risks And Edge Cases
Packed protocol structs must not gain padding or host-endian multi-byte fields without explicit conversion. Message numbers 0-9 are reserved as obsolete and must not be reused. The mixed naming style (`TlSetupRebootMsgAck`) suggests legacy firmware compatibility; renaming would be source-visible. Incorrect version retry behavior in consumers could leave the card unconfigured.

## Test Signals
Protocol tests should validate exact `sizeof` values for every packed message, correct signal numbers on serialized buffers, version retry timeout behavior in the consumer, firmware open/close events reaching channel state, info messages being acknowledged, and reboot messages triggering the reboot callback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/setup_protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/tty.c -->
# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/tty.c

## Purpose
`tty.c` implements the user-visible tty side of the IPWireless driver. It registers the `ttyIPWp` driver, creates modem/monitor/raw tty devices per PCMCIA card, routes user writes to card channels, exposes PPP-related ioctls on the modem tty, manages modem-control lines, and tears down ttys during card removal.

## Important APIs, Types, And Functions
- `struct ipw_tty` wraps `tty_port`, minor index, hardware/network pointers, primary and secondary channel indices, tty type, cached control lines, mutex, and queued TX byte count.
- Minor layout uses 24 minors in three 8-minor ranges: modem, monitor, and optional RAS-raw.
- `ipw_open`, `ipw_close`, and `ipw_hangup` manage open count, `driver_data`, and PPP open/close for modem ttys.
- `ipw_write`, `ipw_write_room`, and `ipw_chars_in_buffer` implement transmit queue accounting against `IPWIRELESS_TX_QUEUE_SIZE`.
- `ipwireless_tty_received` inserts hardware-received data into the tty flip buffer.
- `ipw_ioctl` handles `PPPIOCGCHAN`, `PPPIOCGUNIT`, `FIONREAD`, and `TCFLSH` for modem ttys.
- `ipw_tiocmget`, `ipw_tiocmset`, `get_control_lines`, and `set_control_lines` map Linux modem bits to IPWireless RTS/DTR/CTS/DSR/DCD control lines.
- `ipwireless_tty_create`, `ipwireless_tty_free`, `ipwireless_tty_init`, and `ipwireless_tty_release` manage device and driver lifetime.

## Control Flow And State
Module initialization allocates and registers a dynamic raw tty driver named `ttyIPWp`. Card setup calls `ipwireless_tty_create`, which finds a free slot across all three minor ranges, registers a modem tty associated with dialler and RAS channels, a monitor tty associated with dialler, and a RAS-raw tty associated with RAS. `get_tty` hides RAS-raw minors unless the `loopback` parameter is enabled.

Opening a modem tty starts PPP by calling `ipwireless_ppp_open`; final close or hangup calls `ipwireless_ppp_close`. Writes are serialized by `ipw_tty_mutex`, clipped to remaining transmit queue room, and submitted to hardware on `IPW_CHANNEL_RAS`; the completion callback subtracts sent bytes from `tx_bytes_queued`. Received data is delivered through the flip buffer only when the tty is open. Control-line changes from the network layer update cached bits and hang up the tty when DCD drops.

## State And Persistence Behavior
Global `ttys[24]` stores all active per-minor tty objects, and `ipw_tty_driver` stores the registered tty driver. Per-tty state includes open count, port tty pointer, queued byte count, cached line state, and hardware/network associations. This is all runtime state; no persistent configuration is stored.

## Dependencies And Integration Points
The file depends on Linux tty core, tty flip buffers, serial ioctl structures, PPP ioctls, mutexes, user access helpers, and local hardware/network APIs. It is the main integration point between userspace device nodes, PPP daemon ioctls, and card channel routing.

## Risks And Edge Cases
Several functions have source comments noting uncertain tty locking around `write_room`, modem-control ioctls, and teardown versus parallel ioctl. The send-completion callback updates `tx_bytes_queued` without taking `ipw_tty_mutex`, so accounting can race with writers. `set_control_lines` checks `secondary_channel_idx != -1` even though the field is unsigned, relying on assignment of `-1` as all-bits-set. `ipwireless_tty_create` can leak earlier ttys if a later `add_tty` fails because it returns NULL without rolling back registrations.

## Test Signals
Verify `ttyIPWp*` registration for modem and monitor devices, and raw RAS device visibility only with `loopback=1`. Open/close the modem tty and confirm PPP channel creation/removal. Write near and above 256 KiB queue capacity and confirm clipping/accounting. Toggle RTS/DTR and observe hardware calls on primary and secondary channels. Drop DCD and confirm a tty hangup reaches pppd. Remove the card while ttys are open to exercise vhangup and cleanup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/tty.h -->
# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/tty.h

## Purpose
`tty.h` declares the IPWireless tty-layer interface for `main.c` and `network.c`. It keeps `struct ipw_tty` opaque while exposing driver lifecycle, per-card tty creation/freeing, receive delivery, control-line notification, and modem-type queries.

## Important APIs, Types, And Functions
- `ipwireless_tty_init` and `ipwireless_tty_release` register/unregister the global `ttyIPWp` driver.
- `ipwireless_tty_create` creates the per-card modem, monitor, and raw tty objects.
- `ipwireless_tty_free` removes all tty objects associated with a card.
- `ipwireless_tty_received` delivers channel data into a tty flip buffer.
- `ipwireless_tty_is_modem` identifies whether a tty is the PPP modem tty.
- `ipwireless_tty_notify_control_line_change` updates modem-control state and handles DCD drop behavior.

## Control Flow And State
The header has no control flow. It defines the callbacks used by network receive/control paths and by top-level PCMCIA lifecycle code. `main.c` calls init/release and create/free; `network.c` calls receive, modem detection, and control-line notification.

## State And Persistence Behavior
The tty object is opaque. Its implementation stores tty-port state, channel associations, line status, and transmit accounting. All state is runtime-only and tied either to module lifetime or card lifetime.

## Dependencies And Integration Points
The header depends on Linux types and local opaque `ipw_hardware`/`ipw_network` declarations through included headers. It integrates userspace tty devices with the card channel router and PPP network path.

## Risks And Edge Cases
Callers must respect lifetime ordering: `ipwireless_tty_free` is documented as needing to run before `ipwireless_network_free`, because tty cleanup disassociates from network channel arrays. `ipwireless_tty_received` assumes the passed tty remains valid for the duration of delivery. Control-line notifications can trigger hangup, so callers must be prepared for reentrant tty teardown behavior.

## Test Signals
Build coverage should catch signature mismatches between `tty.c`, `network.c`, and `main.c`. Runtime signals include correct device creation/free ordering, safe receive delivery while ttys are open or closed, modem detection causing RAS data to route to PPP only for the modem tty, and DCD drop causing tty hangup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/ipwireless/tty.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/mips_ejtag_fdc.c -->
# sources/distributed-fs/ceph-client/drivers/tty/mips_ejtag_fdc.c

## Purpose
`mips_ejtag_fdc.c` implements tty, console, early-console, and optional KGDB support for MIPS EJTAG Fast Debug Channels. It exposes up to 16 per-CPU debug channels as raw ttys, encodes byte streams into FDC words, drains RX from the hardware FIFO, writes TX asynchronously from a CPU-pinned kthread, and supports IRQ or polling operation.

## Important APIs, Types, And Functions
- Register macros define FDC access, configuration, status, RX, and per-channel TX registers plus FIFO and interrupt threshold fields.
- `struct fdc_word`, `mips_ejtag_fdc_encode`, and `mips_ejtag_fdc_decode` implement compact 1-to-4-byte packing into 32-bit FDC words.
- `struct mips_ejtag_fdc_tty_port` stores tty port state, RX buffer lock/buffer, circular TX buffer pointers, and completion for empty TX.
- `struct mips_ejtag_fdc_tty` stores device-wide state: CPU, register mapping, per-channel ports, waitqueue, writer thread, FIFO sizes, IRQ/polling state, and optional sysrq state.
- Console functions `mips_ejtag_fdc_console_write`, `mips_ejtag_fdc_console_device`, and `mips_ejtag_fdc_console_init` support normal and early console output.
- Data path functions include `mips_ejtag_fdc_put`, `mips_ejtag_fdc_put_chan`, `mips_ejtag_fdc_handle`, `mips_ejtag_fdc_isr`, and `mips_ejtag_fdc_tty_timer`.
- TTY operations include install/open/close/hangup/write/write-room/chars-in-buffer and tty-port activate/shutdown.
- Probe/hotplug hooks are `mips_ejtag_fdc_tty_probe`, `mips_ejtag_fdc_tty_cpu_down`, and `mips_ejtag_fdc_tty_cpu_up`.

## Control Flow And State
Console initialization runs early via `console_initcall`, probing CDMM type `0xfd` and registering an `fdc` console. Device probe maps registers, reads FIFO sizing, disables FDC interrupts, allocates a 16-minor raw tty driver for one CPU, initializes every tty port and buffer lock, stores console register pointers, starts a writer kthread pinned to the FDC CPU, and either enables RX interrupts or starts a pinned polling timer.

Writes from tty users enter a per-port circular buffer under `xmit_lock`, update the aggregate `xmit_total`, and wake the writer thread. The kthread waits for data and TX FIFO space, enables TX-not-full interrupts when needed, selects non-empty channels round-robin, encodes up to four bytes into an FDC word, writes the per-channel TX register, updates buffer pointers, and wakes tty writers when space becomes available.

RX handling is shared by IRQ and timer paths. `mips_ejtag_fdc_handle` drains FDC RX words, selects the target channel from status, decodes bytes, handles optional KGDB Ctrl-C and console sysrq sequences, inserts bytes into the port flip buffer if the port is active, then disables TX interrupts and wakes the writer when TX FIFO space returns.

## State And Persistence Behavior
Per-device runtime state includes mapped FDC registers, per-channel tty ports, TX circular buffers, RX buffers allocated only while a port is active, interrupt configuration bits, and polling timer state. Console register pointers are cached per CPU and reused by early console/KGDB setup. There is no disk persistence; hardware register configuration persists until CPU down/remove or reprogramming.

## Dependencies And Integration Points
The driver depends on MIPS CDMM discovery, CP0 FDC interrupt cause bits, Linux tty/console/kgdb/sysrq APIs, kthreads, timers, raw spinlocks for non-threadable IRQ paths, and per-CPU IRQ constraints. It registers as a built-in MIPS CDMM driver for type `0xfd`.

## Risks And Edge Cases
The FDC interrupt may be shared and is not individually maskable, so the driver uses `IRQF_NO_THREAD` and raw locks; RT behavior depends on keeping ISR work bounded. Console writes busy-wait for FIFO space with interrupts disabled locally. Polling mode must keep timers pinned to the correct CPU because channels are per-CPU. TX shutdown waits for pending data to drain, so a stuck FIFO could delay close. `mxser_tx_empty`-style inversion is not present here, but FDC TX-full races with console output are handled by rechecking status before writes.

## Test Signals
Validate console and early console output on each CPU, tty registration as `ttyFDC*`, RX/TX traffic on multiple channels with round-robin fairness, fallback polling when no IRQ is available, CPU down/up restarting timers and kthreads, sysrq on console Ctrl-O, KGDB Ctrl-C on the configured channel, and clean close/remove with no live timer or kthread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/mips_ejtag_fdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/moxa.c -->
# sources/distributed-fs/ceph-client/drivers/tty/moxa.c

## Purpose
`moxa.c` implements the firmware-backed MOXA Intellio C218/C320/CP-204J multiport serial driver. It loads board firmware into dual-ported RAM, configures per-port shared-memory ring tables, registers `ttyMX` devices, polls firmware interrupt/status tables, and exposes tty operations for data, modem control, termios, break, and serial settings.

## Important APIs, Types, And Functions
- Large macro groups define firmware function codes, shared-memory table offsets, interrupt bits, flow-control bits, and ring-buffer page layouts for C218 and C320 variants.
- `struct moxa_board_conf` stores board type, port count, readiness, ports, mapped base memory, and interrupt table pointers.
- `struct moxa_port` wraps `tty_port`, board pointer, firmware table address, UART type, cflag, status flags, DCD state, line-control cache, and low-water flag.
- Firmware loading functions are `moxa_check_fw_model`, `moxa_load_bios`, `moxa_load_320b`, `moxa_real_load_code`, `moxa_load_code`, `moxa_load_fw`, and `moxa_init_board`.
- PCI/module hooks are `moxa_pci_probe`, `moxa_pci_remove`, `moxa_init`, and `moxa_exit`.
- TTY operations include `moxa_open`, `moxa_close`, `moxa_write`, `moxa_write_room`, `moxa_flush_buffer`, `moxa_chars_in_buffer`, `moxa_set_termios`, stop/start, hangup, break, and modem-control getters/setters.
- Low-level port functions include `MoxaPortEnable`, `MoxaPortDisable`, `MoxaPortSetTermio`, `MoxaPortWriteData`, `MoxaPortReadData`, queue depth helpers, TX enable/disable, and `MoxaSetFifo`.

## Control Flow And State
Module initialization registers a dynamic raw `ttyMX` driver and then the PCI driver. Probe enables the PCI device, reserves BAR 2, maps 16 KiB of board memory, chooses an initial port count, allocates port objects, requests firmware by board type, downloads BIOS and communication code, initializes firmware ring-buffer page/mask fields for each port, marks the board ready, starts the global polling timer if needed, and registers tty devices.

Open validates board readiness and port number under `moxa_openlock`, increments the port count, assigns tty driver data, initializes termios/hardware on first open, enables the port, and then blocks until carrier as directed by tty-port helpers. Writes copy data into firmware TX rings under `moxa_lock` and mark low-water wakeup state. The global timer `moxa_poll` scans ready boards, checks firmware interrupt-pending state, polls every port for TX wakeups, RX data, break, and DCD changes, acknowledges firmware interrupt tables, handles low-water XON checks, and re-arms itself while any board is served.

Remove marks the board not ready, hangs up initialized ports, waits for open users to drain, unregisters tty devices, unmaps BAR memory, and frees ports.

## State And Persistence Behavior
Persistent hardware/firmware state lives in board dual-ported RAM: firmware image, magic/status fields, per-port ring pointers, page assignments, flow control, line status, and interrupt tables. Kernel runtime state includes the global board array, polling timer, firmware timeout, per-port status bits (`TXSTOPPED`, `LOWWAIT`, `EMPTYWAIT`), DCD cache, and line-control cache. No host filesystem state is written beyond firmware loading through the kernel firmware API.

## Dependencies And Integration Points
The driver depends on PCI, firmware loading, MMIO accessors, Linux tty core, tty flip buffers, timers, locking helpers, and serial structures. It integrates with external firmware files `c218tunx.cod`, `cp204unx.cod`, and `c320tunx.cod`. Unlike `mxser`, data movement is through shared memory rings and firmware function commands rather than direct UART register interrupt handling.

## Risks And Edge Cases
Firmware loading uses long sleeps and polling handshakes; bad firmware length, model mismatch, checksum failure, or missing magic values abort probe. Polling holds `moxa_lock` while scanning boards and moving data, so large bursts across many ports can increase latency. Shared-memory ring math differs by board type and port count; incorrect page/mask values can corrupt adjacent rings. `moxa_board_deinit` destroys ports before waiting for initialized users to disappear, so hot-unplug relies on tty hangup behavior and the open lock. The driver has no real IRQ handler; timer cadence controls latency.

## Test Signals
Probe each supported PCI ID with matching and mismatched firmware, confirm board ready logs and expected port counts, verify `ttyMX` device registration/unregistration, run RX/TX loopback across ports, test CLOCAL/carrier blocking and DCD hangup, exercise break delivery, termios changes, hardware/software flow control, TX low-water wakeups, hot-unplug with open ports, and missing firmware failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/moxa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/mxser.c -->
# sources/distributed-fs/ceph-client/drivers/tty/mxser.c

## Purpose
`mxser.c` implements the MOXA Smartio/Industio PCI multiport serial driver for direct UART-style boards. It supports many MOXA PCI IDs, registers `ttyMI` devices, programs standard and MOXA MUST enhanced UARTs, handles shared IRQ dispatch across board ports, and exposes tty operations, modem ioctls, flow control, RS-232/422/485 operation-mode ioctls, and serial settings.

## Important APIs, Types, And Functions
- PCI ID table entries encode port counts and a high-baud exception bit.
- MOXA MUST helpers such as `mxser_must_select_bank`, `mxser_must_set_enhance_mode`, `mxser_set_must_fifo_value`, and `mxser_must_get_hwid` access enhanced register banks for MU150/MU860 devices.
- `struct mxser_board` stores board index, port count, IRQ, interrupt-vector I/O address, MUST hardware ID, max baud, and flexible-array ports.
- `struct mxser_port` stores `tty_port`, I/O addresses, FIFO thresholds, UART type, cached IER/MCR/FCR, optional XON/XOFF char, interrupt counters, timeout, status masks, FIFO size, and spinlock.
- TTY lifecycle/data functions include `mxser_open`, `mxser_activate`, `mxser_close`, `mxser_shutdown_port`, `mxser_write`, `mxser_put_char`, `mxser_flush_chars`, stop/start, hangup, break, and wait-until-sent.
- Configuration/ioctl functions include `mxser_change_speed`, `mxser_set_baud`, `mxser_set_serial_info`, `mxser_get_serial_info`, `mxser_ioctl`, `mxser_ioctl_op_mode`, `mxser_tiocmget`, `mxser_tiocmset`, and `mxser_get_icount`.
- Interrupt data paths are `mxser_interrupt`, `mxser_port_isr`, `mxser_receive_chars`, `mxser_receive_chars_new`, `mxser_receive_chars_old`, `mxser_transmit_chars`, and `mxser_check_modem_status`.

## Control Flow And State
Module initialization allocates/registers a dynamic raw `ttyMI` driver and registers the PCI driver. Probe claims a board slot, enables the PCI device with managed PCI helpers, reserves BAR 2 for port I/O and BAR 3 for interrupt-vector/operation-mode registers, assigns port I/O bases spaced eight bytes apart, detects MUST hardware from the first port, initializes per-port tty ports and spinlocks, disables interrupts, requests a shared IRQ, and registers tty devices.

Opening a tty attaches `driver_data` and delegates to `tty_port_open`; activation allocates the transmit kfifo buffer, validates UART presence, clears FIFOs and interrupt/status registers, initializes LCR/MCR/IER, resets the kfifo, and applies current termios. Writes enqueue into the tty-port xmit kfifo under the port spinlock and enable transmit interrupts when appropriate. The shared ISR reads the board vector register to find ports with pending interrupts, loops with pass limits, and calls per-port ISR logic under each port lock.

Receive handling has a fast path for MUST good-data-length mode when no error bits are present; otherwise it reads byte-by-byte, applies read/ignore masks, updates async error counters, handles break/SAK, and pushes the flip buffer. Transmit handling sends a pending XON/XOFF char first, then drains up to the hardware FIFO size from the kfifo, wakes tty writers below `WAKEUP_CHARS`, and disables THRI when empty. Modem status changes update counters, wake `TIOCMIWAIT`, handle carrier-open wait, and enforce CTS flow control.

## State And Persistence Behavior
Hardware state is direct UART/MUST register state: divisor latches, LCR/MCR/IER/FCR, software-flow-control registers, FIFO thresholds, operation-mode registers for MU860 RS-232/422/485 selection, and interrupt vector bits. Kernel runtime state includes the board bitmap, per-port cached control registers, kfifo contents, tty-port flags, async counters, timeout estimates, and masks derived from termios. No persistent host storage is used.

## Dependencies And Integration Points
The driver depends on PCI, port I/O accessors, Linux tty core, tty-port kfifo support, serial core constants, shared IRQ handling, wait queues, and capability checks for privileged serial settings. It integrates with userspace through `ttyMI*`, standard serial ioctls, `TIOCMIWAIT`, `TIOCGICOUNT`, and legacy MOXA operation-mode ioctls.

## Risks And Edge Cases
MUST enhanced register access temporarily writes magic LCR/EFR bank values and must restore LCR correctly. Shared IRQ dispatch uses vector bits where a clear bit indicates a pending port, and pass limits avoid livelock. `mxser_tx_empty` returns the inverse of TEMT despite its name, so wait logic depends on that exact behavior. `mxser_ioctl_op_mode` returns `-EFAULT` when the hardware is not MU860, which is semantically odd. Throttle/unthrottle modifies IER/MCR without always taking the same lock in all paths. Probe cleanup must unregister already registered tty devices and clear the board bitmap.

## Test Signals
Validate probe/remove for representative 2-, 4-, and 8-port boards, including high-baud CP-102 variants and MU150/MU860 detection. Exercise baud changes including `BOTHER`, FIFO threshold programming, software and hardware flow control, `TIOCMIWAIT`/`TIOCGICOUNT`, RS-485/RS-422 operation-mode ioctls on MU860, RX error and break accounting, TX wakeups below `WAKEUP_CHARS`, shared IRQ storms with pass-limit behavior, and open failure when UART LSR reads `0xff`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/mxser.c -->
