# Research: subset-b-005509

Grouped research for USB host controller sources under `sources/distributed-fs/ceph-client/drivers/usb/host`. Each file section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-hcd.c

## Purpose
`fhci-hcd.c` is the Linux USB HCD platform driver for the Freescale QUICC Engine USB Host Controller Interface. It wires the FHCI implementation into `struct hc_driver`, allocates FHCI software state, maps QE USB registers and multi-user RAM parameter RAM, requests QE pins/GPIOs/timer IRQs, and starts/stops the controller.

## Important APIs, Types, and Functions
- HCD lifecycle: `fhci_start()`, `fhci_stop()`, `fhci_urb_enqueue()`, `fhci_urb_dequeue()`, `fhci_endpoint_disable()`, and `fhci_get_frame_number()` populate `fhci_driver`.
- Controller setup: `of_fhci_probe()` validates device-tree mode, creates the HCD, maps registers, allocates FHCI PRAM with `cpm_muram_alloc()`, requests GPIO descriptors, QE pins, GTM timer, clock sources, and USB IRQ, then calls `usb_add_hcd()`.
- Low-level helpers: `fhci_start_sof_timer()`, `fhci_stop_sof_timer()`, `fhci_get_sof_timer_count()`, `fhci_usb_enable_interrupt()`, `fhci_usb_disable_interrupt()`, and `fhci_ioports_check_bus_state()`.
- Memory/lifetime helpers: `fhci_mem_init()`, `fhci_mem_free()`, `fhci_create_lld()`, `fhci_usb_init()`, and `fhci_usb_free()`.

## Control Flow
Probe exits early when USB is disabled or device-tree `mode` is not `host`. After HCD allocation, probe maps the USB register resource, allocates and assigns QE parameter RAM, gathers GPIOs/pins, obtains a 16-bit GTM timer and IRQ, maps the USB IRQ, resolves optional full-/low-speed clock names, programs initial transceiver speed, clears interrupt state, and registers the HCD. `fhci_start()` then allocates controller lists/root hub/TD and ED pools, creates the low-level `fhci_usb`, initializes PRAM/registers and endpoint zero, initializes the virtual root hub, marks the HCD running, and enables the controller. URB enqueue computes TD count by pipe type, allocates `urb_priv`, links the URB to the USB core endpoint, initializes URB state, and delegates transfer construction to `fhci_queue_urb()`. Stop disables interrupts/controller, frees endpoint zero and low-level state, and recycles software memory.

## State and Persistence Behavior
Runtime state is entirely in kernel memory and device registers: `fhci_hcd`, `fhci_usb`, virtual root hub fields, ED/TD free lists, QE PRAM, and hardware registers. Interrupt nesting is tracked with `intr_nesting_cnt`; `saved_msk` persists the desired USB interrupt mask across disable/enable windows. No disk persistence exists. The source assumes the HCD spinlock protects URB, endpoint, and root-hub mutable state.

## Dependencies and Integration Points
The file depends on Linux USB HCD APIs, OF/platform-device APIs, QE/CPM MURAM helpers, GTM timer helpers, GPIO descriptors, and FHCI sibling files for hub, scheduler, queue, memory, and TD-ring behavior. Device-tree properties include `mode`, `hub-power-budget`, `reg`, GPIO indices, QE pin indices, `fsl,fullspeed-clock`, and `fsl,lowspeed-clock`.

## Risks and Test Signals
Risks include fragile interrupt nesting balance, error-path resource unwinding across PRAM/pins/timer/IRQ/HCD, assumptions about GPIO ordering and optional speed/power GPIOs, and TD-count sizing for zero-length or zero-packet URBs. Useful test signals are probe/remove on real QE hardware or DT emulation, enumeration at full and low speed, control/bulk/interrupt/iso URB enqueue/dequeue, disconnect during active URBs, endpoint disable while TDs are queued, and injected failures for MURAM, timer IRQ, GPIO, pin, and clock acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-hub.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-hub.c

## Purpose
`fhci-hub.c` implements the FHCI virtual root hub and the physical single-port transceiver controls behind it. It translates USB core hub requests into virtual hub status changes, QE GPIO transceiver configuration, port reset signaling, SOF timer control, and FHCI port enable/disable behavior.

## Important APIs, Types, and Functions
- Root hub callbacks exported to `fhci_driver`: `fhci_hub_status_data()` and `fhci_hub_control()`.
- Port and transceiver operations: `fhci_config_transceiver()`, `fhci_port_disable()`, `fhci_port_enable()`, `fhci_io_port_generate_reset()`, and `fhci_port_reset()`.
- `root_hub_des` describes a one-port USB hub with individual port power switching and no over-current protection.

## Control Flow
Hub status checks inspect `vroot_hub->port.wPortChange` under the FHCI lock and report bit 1 for the single downstream port. Hub control handles standard USB hub requests. `GetHubDescriptor`, `GetHubStatus`, and `GetPortStatus` return virtual structures. `SetPortFeature(POWER)` powers the transceiver and enters waiting state. `SetPortFeature(RESET)` sets reset status, calls `fhci_port_reset()`, enables the port, and clears reset. `SetPortFeature(ENABLE)` calls `fhci_port_enable()`. Clear-feature paths clear virtual status/change bits and may disable port power, stop SOF, or disable the port.

Physical reset disables SOF and the USB controller, masks idle interrupts, drives USBOE/USBTP/USBTN GPIOs low for reset, restores them to dedicated QE pins, restores interrupts, re-enables the controller, and restarts SOF. Port disable stops SOF, flushes transmissions, masks interrupts, switches `port_status` to disabled, enables IDLE detection for future connect, updates virtual hub enable-change bits, and re-enables interrupts.

## State and Persistence Behavior
State is maintained in `fhci_usb->port_status`, `fhci->vroot_hub`, `saved_msk`, transceiver GPIO outputs, QE pin mux state, and USB mode/mask registers. The virtual root hub is volatile and reconstructed during HCD start. GPIO power/speed values may persist electrically until changed by remove or platform reset.

## Dependencies and Integration Points
This file integrates Linux USB hub request constants, GPIO descriptor operations, QE pin muxing, FHCI scheduler/TD flush functions, and FHCI SOF timer helpers. It depends on `fhci_ioports_check_bus_state()` and device connect/disconnect handling in `fhci-sched.c` for connection detection after IDLE/RESET events.

## Risks and Test Signals
Risks include sleeping `mdelay()` calls while called under the HCD spinlock from hub control, assumptions about one-port topology, subtle saved interrupt mask updates, GPIO polarity/ordering mistakes, and races between disable/reset and simultaneous connect events. Test signals include hub descriptor correctness, hub status bitmap on connect/enable/reset/suspend/power changes, reset timing with enumeration, optional speed/power GPIO absence, and disconnect/reconnect during port disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-mem.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-mem.c

## Purpose
`fhci-mem.c` owns FHCI software ED/TD object initialization, free-list recycling, and TD population. It is the allocator-facing layer used by URB scheduling to avoid repeated dynamic allocation in normal interrupt-driven paths.

## Important APIs, Types, and Functions
- `fhci_recycle_empty_td()` and `fhci_recycle_empty_ed()` reset and return TD/ED objects to controller free lists.
- `fhci_get_empty_ed()` and internal `get_empty_td()` remove objects from free lists or allocate fallback objects with `GFP_ATOMIC`.
- `fhci_td_fill()` initializes a TD for a URB stage and stores it in `urb_priv->tds[index]`.
- Internal `init_td()` and `init_ed()` zero objects and initialize list heads.

## Control Flow
At controller start, `fhci_mem_init()` in `fhci-hcd.c` preallocates `MAX_TDS` and `MAX_EDS` and recycles them through these helpers. URB construction in `fhci_queue_urb()` calls `fhci_td_fill()` for setup/data/status, bulk fragments, interrupt TDs, or iso packet descriptors. Each TD captures the URB, ED, transaction type, data pointer, length, toggle, iso index, interval, start frame, IOC flag, and initial OK status. Completion paths recycle TDs and EDs through the reset helpers.

## State and Persistence Behavior
The persistent state is the controller's in-memory `empty_tds` and `empty_eds` lists. Recycling deliberately clears prior runtime fields such as packet pointers, counters, statuses, and list links, which prevents stale TD/ED state from contaminating later URBs. There is no external persistence.

## Dependencies and Integration Points
The file depends on `fhci.h` structures, kernel slab/list APIs, and FHCI queue/scheduler code. It assumes callers hold the appropriate FHCI lock when manipulating shared lists. Fallback `GFP_ATOMIC` allocation allows continued operation if the preallocated pool is exhausted, but logs allocation failures with `fhci_err()`.

## Risks and Test Signals
Risks include pool exhaustion under many active URBs, unchecked `fhci_td_fill()` failures in callers, and dependence on correct object recycling order. Test signals include stress enqueue/dequeue beyond `MAX_TDS`/`MAX_EDS`, allocation-failure injection, repeated endpoint disable/reuse cycles, and verifying that recycled TDs do not retain stale `frame_lh`, `pkt`, `error_cnt`, or `nak_cnt` state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-q.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-q.c

## Purpose
`fhci-q.c` implements FHCI software queue manipulation and URB completion accounting. It maps FHCI TD hardware/status bits to Linux errno values, moves TDs among ED queues, frame queues, and the done list, updates URB lengths/statuses, and returns completed URBs to the USB core.

## Important APIs, Types, and Functions
- Queue operations: `fhci_add_tds_to_ed()`, `fhci_remove_td_from_ed()`, `fhci_add_td_to_frame()`, `fhci_remove_td_from_frame()`, `fhci_peek_td_from_frame()`, `fhci_remove_td_from_done_list()`, and `fhci_move_td_from_ed_to_done_list()`.
- Completion operations: `fhci_done_td()`, `fhci_urb_complete_free()`, and `fhci_del_ed_list()`.
- `status_to_error()` converts FHCI TD status bits into USB core status codes.

## Control Flow
URB queueing appends all TDs to an ED and sets `td_head` if idle. Scheduling moves a TD into the actual frame and, when hardware completion is confirmed, `fhci_move_td_from_ed_to_done_list()` removes the current head, advances the ED, updates toggle carry, appends the TD to `done_list`, and schedules the completion tasklet if IOC is set. The tasklet calls `fhci_done_td()` for each done TD, increments the URB completed-TD count, and either gives the URB back or handles delete/halt cleanup. Dequeue paths mark URBs for deletion and `fhci_del_ed_list()` removes TDs from EDs when safe.

## State and Persistence Behavior
Mutable state lives in linked lists (`ed->td_list`, `frame->tds_list`, `hc_list->done_list`), ED fields (`td_head`, `state`, `toggle_carry`), URB private counters, and URB aggregate status/actual length. `fhci_urb_complete_free()` recycles TDs, possibly removes idle EDs from schedules, decrements `active_urbs`, unlinks the URB from the USB core endpoint, drops the FHCI lock for `usb_hcd_giveback_urb()`, and reacquires it.

## Dependencies and Integration Points
The file integrates with FHCI scheduler completion, memory recycling, USB HCD endpoint linking/unlinking, and Linux URB semantics such as `URB_SHORT_NOT_OK`, iso frame descriptors, and endpoint toggles. It assumes lock ownership around list mutations and uses completion status values defined in `fhci.h`.

## Risks and Test Signals
Risks include list corruption if TDs are removed twice, lock reentry hazards around giveback, missing handling for null/stale `urb_priv` during asynchronous dequeue, and subtle short-packet semantics for control/bulk/iso. Test signals include short reads with and without `URB_SHORT_NOT_OK`, stall/NAK/timeout/error mapping, iso descriptor status updates, interrupt URB unlink, endpoint disable during active TDs, and active URB count returning to zero after stress cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-sched.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-sched.c

## Purpose
`fhci-sched.c` is the FHCI transaction scheduler and interrupt engine. It converts queued ED/TD work into per-frame packets, enforces frame byte/time limits, handles SOF/timer/USB events, detects connect/disconnect, and schedules the tasklet that gives completed URBs back to the USB core.

## Important APIs, Types, and Functions
- Scheduler: `fhci_schedule_transactions()`, `scan_ed_list()`, `add_packet()`, `rotate_frames()`, and `fhci_flush_all_transmissions()`.
- Completion: `fhci_transaction_confirm()`, `process_done_list()`, `fhci_transfer_confirm_callback()`.
- Interrupts/events: `fhci_irq()`, `fhci_frame_limit_timer_irq()`, `sof_interrupt()`, `fhci_device_connected_interrupt()`, and `fhci_device_disconnected_interrupt()`.
- URB construction: `fhci_queue_urb()` builds EDs and TD chains for all supported pipe types.

## Control Flow
Each SOF starts or transmits the current frame, arms the GTM frame-limit timer, and asks the scheduler to fill remaining frame budget. Scheduling scans iso, interrupt, control, then bulk lists. `add_packet()` computes packet length/data pointer/toggle, rejects work when byte or time budget is exhausted, obtains a packet object, handles dummy receive buffers, adds the TD to the frame list, and submits the hardware transaction. Hardware completion eventually calls `fhci_transaction_confirm()`, which removes the matching frame TD, copies dummy IN data, classifies NAK/errors/shorts, updates toggles and lengths, and moves complete TDs to the done list. The tasklet drains the done list and gives back URBs or continues deletion/halt cleanup.

Connection IRQ flow reads GPIO line state, programs QE clock for low/full speed, sets low-speed mode bits, updates virtual hub status/change flags, computes max bytes per frame, and enables the port. Disconnect clears connection state, stops SOF, enables IDLE detection, and sets the virtual hub connection-change bit.

## State and Persistence Behavior
Primary state includes `actual_frame` fields (`frame_num`, `total_bytes`, `frame_status`, TD list), endpoint lists by transfer type, ED scheduling state, TD retry counters, port status, virtual hub fields, interrupt masks, and the FHCI tasklet. State is volatile; consistency depends on the FHCI spinlock plus explicit IRQ disable/enable around the tasklet and hardware descriptor access.

## Dependencies and Integration Points
This file sits between USB HCD URBs, FHCI queue/memory helpers, `fhci-tds.c` hardware descriptor operations, QE clock and timer APIs, GPIO bus-state sampling, and virtual root hub updates. It also depends on Linux tasklets and IRQ handling.

## Risks and Test Signals
Risks include frame-budget miscalculation, stale actual-frame TDs requiring flush, race-prone interrupt masking inside interrupt context, a FIXME around iso frame-counter rollover, NAK/retry behavior that can affect bulk fairness, and disconnect during in-flight hardware transactions. Test signals include heavy mixed iso/interrupt/control/bulk traffic, frame-limit timer expiry, MSF aborts, NAK storms, repeated short IN packets, low-speed/full-speed connect detection, unplug during active transfer, and tasklet completion under concurrent unlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-tds.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-tds.c

## Purpose
`fhci-tds.c` owns FHCI endpoint-zero hardware transfer descriptors and packet FIFO plumbing. It allocates CPM MURAM descriptor rings, initializes endpoint parameter RAM, submits packet descriptors to hardware, confirms completed buffer descriptors, maps hardware descriptor errors to FHCI packet statuses, and flushes rings on abort/reset.

## Important APIs, Types, and Functions
- Hardware TD format: local `struct usb_td` and TD bit definitions (`TD_R`, `TD_W`, `TD_I`, `TD_TC`, token/status/error bits).
- Endpoint lifecycle: `fhci_create_ep()`, `fhci_init_ep_registers()`, and `fhci_ep0_free()`.
- Submission/completion: `fhci_host_transaction()`, `fhci_tx_conf_interrupt()`, `fhci_host_transmit_actual_frame()`, and internal `fhci_td_transaction_confirm()`.
- Flush/control helpers: `fhci_flush_bds()`, `fhci_flush_actual_frame()`, and `fhci_push_dummy_bd()`.

## Control Flow
Endpoint creation allocates a combined MURAM area for the TD ring and endpoint PRAM, allocates three pointer FIFOs for confirmation frames, empty frames, and dummy receive buffers, initializes packet/buffer pools, sets wrap on the last descriptor, and stores the endpoint in `usb->ep0`. Register initialization programs endpoint mode, PRAM pointers, function codes, buffer lengths, and TX ring base pointers.

`fhci_host_transaction()` temporarily disables FHCI interrupts, reserves the next empty descriptor, writes the physical data address, token/address/endpoint/type fields, status bits, low-speed PRE behavior, and length, queues the packet in `conf_frame_Q`, and starts the FIFO if this is the first queued frame. Completion scans `conf_td` descriptors that are no longer ready, clears them, skips dummy markers, dequeues the corresponding packet, translates descriptor errors and IN lengths, and calls `fhci_transaction_confirm()`. Flush paths mark ready descriptors timed out, consume confirmations, reset descriptor contents and PRAM pointers, and restore ring cursors.

## State and Persistence Behavior
Persistent runtime state is the endpoint object: MURAM TD ring, endpoint PRAM pointer, ring cursors (`conf_td`, `empty_td`), three kfifos, and `already_pushed_dummy_bd`. Descriptor state is shared with hardware and must be accessed through big-endian I/O helpers. No disk state exists.

## Dependencies and Integration Points
The file depends on CPM MURAM allocation/address translation, FHCI queue helpers (`cq_*`), scheduler confirmation callbacks, QE USB command registers, and Linux physical address translation via `virt_to_phys()`. It is tightly coupled to endpoint zero in this FHCI implementation.

## Risks and Test Signals
Risks include DMA/physical-address assumptions for packet buffers, descriptor-ring wrap/cursor desynchronization, dummy descriptor handling bugs, FIFO exhaustion, and error mapping differences between RX and TX failures. Test signals include IN/OUT/SETUP transfers at ring boundaries, dummy IN receive path, descriptor full condition, TX error/timeout/NAK/stall injection, flush during active descriptors, and repeated create/free cycles under allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-tds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/fhci.h

## Purpose
`fhci.h` is the shared contract for the Freescale QUICC Engine FHCI driver. It defines hardware register/descriptor constants, packet and TD status encodings, controller data structures, endpoint/URB/frame state models, FIFO helpers, logging helpers, HCD conversion helpers, and cross-file function prototypes.

## Important APIs, Types, and Functions
- Hardware-facing structures: `struct fhci_pram`, `struct fhci_ep_pram`, and local register/bit definitions for USB mode, endpoint, command, event, bus mode, and packet metadata.
- Software state: `struct fhci_hcd`, `struct fhci_usb`, `struct virtual_root_hub`, `struct endpoint`, `struct ed`, `struct td`, `struct packet`, `struct urb_priv`, and `struct fhci_time_frame`.
- Enumerations: GPIO/pin indices, transfer type/mode, speed, ED state, port status, and memory allocation target.
- Helpers: `get_frame_num()`, `hcd_to_fhci()`, `fhci_to_hcd()`, logging macros, and pointer FIFO wrappers `cq_new()`, `cq_put()`, `cq_get()`, etc.

## Control Flow Role
The header does not execute control flow directly, but it defines the state machine shared by the implementation files. URBs are broken into `td` objects attached to an `ed`; TDs are scheduled into `fhci_time_frame`; frames are converted into hardware packets; completed packets set TD status; done TDs feed URB giveback. Port state transitions flow through `FHCI_PORT_POWER_OFF`, `DISABLED`, `WAITING`, `FULL`, `LOW`, and transient disconnecting states.

## State and Persistence Behavior
The header distinguishes persistent per-controller state (`fhci_hcd`, `fhci_usb`, ED/TD pools), per-endpoint state (`ed`, `endpoint`), per-URB state (`urb_priv`), and per-frame state (`fhci_time_frame`). All are volatile kernel structures. Hardware state is represented through big-endian I/O memory pointers and CPM MURAM offsets.

## Dependencies and Integration Points
Includes Linux kernel, USB HCD, kfifo, GPIO descriptor, QE, and immap headers. It is included by all FHCI implementation files and exposes prototypes for the HCD, hub, memory, queue, scheduler, TD, and optional debugfs pieces.

## Risks and Test Signals
Risks include ABI-like coupling between files, fixed pool constants (`MAX_EDS`, `MAX_TDS`), bitmask overlap mistakes, assumptions around pointer-sized kfifo entries, and legacy tasklet/API patterns. Test signals are mostly compile-time and integration-oriented: all FHCI files must agree on structure fields and prototypes; sparse/endian checking should validate I/O accesses; runtime stress should confirm ED/TD state transitions and status-bit mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fsl-mph-dr-of.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/fsl-mph-dr-of.c

## Purpose
`fsl-mph-dr-of.c` is Freescale USB2 device-tree glue. It reads flat device-tree properties for multi-port host and dual-role USB controllers, creates child platform devices for the appropriate host/OTG/device drivers, fills `struct fsl_usb2_platform_data`, and supplies MPC512x-specific PHY/clock initialization hooks.

## Important APIs, Types, and Functions
- Mode data: `struct fsl_usb2_dev_data` and `dr_mode_data[]` map `dr_mode` to child driver names and operating modes.
- Parsing/helpers: `get_dr_mode_data()`, `determine_usb_phy()`, and `usb_get_ver_info()`.
- Child registration: `fsl_usb2_device_register()` allocates a platform device, copies resources/platform data, inherits DMA mask and OF node, and registers it.
- Driver lifecycle: `fsl_usb2_mph_dr_of_probe()`, `fsl_usb2_mph_dr_of_remove()`, and `__unregister_subdev()`.
- MPC512x support: `fsl_usb2_mpc5121_init()`, `fsl_usb2_mpc5121_exit()`, and `fsl_usb2_mpc5121_pd`.

## Control Flow
Probe verifies device availability and match data, copies compatible-specific platform data, selects host/otg/peripheral mode, applies MPH port-enable flags or DR polarity flags, parses PHY type and controller version, reads erratum booleans and `phy-clk-valid`, and rejects sysif-register configurations without a known controller version. It then iterates selected child driver names and registers each child using the parent resources. Remove unregisters all children.

For MPC512x, the init callback obtains/enables the `ipg` clock and, for UTMI-wide PHY mode, programs USBGENCTRL/ISIPHYCTRL bits for PHY enable, oscillator enable, and polarity settings. Exit disables the clock and clears `regs`.

## State and Persistence Behavior
The file stores no long-lived private object beyond static child index `idx` and platform data copied into child devices. Parsed flags persist as child platform data until device unregister. Hardware register effects from MPC512x init persist until child exit or reset.

## Dependencies and Integration Points
It depends on Linux OF/platform-device/DMA/clock APIs and Freescale USB platform definitions from `linux/fsl_devices.h`. It instantiates drivers named `fsl-ehci`, `fsl-usb2-otg`, and `fsl-usb2-udc`, passing parent resources and OF association to children.

## Risks and Test Signals
Risks include fallback to host mode on invalid/missing `dr_mode`, static `idx` reuse behavior across devices/probe cycles, resource sharing among multiple child devices, property spelling differences for errata (`usb-erratum` vs `usb_erratum`), and missing cleanup if registering later children fails after earlier ones succeeded. Test signals include DT matrices for MPH/DR/OTG/peripheral, controller version compatibles, PHY modes, erratum flags, MPC512x clock failure paths, child device counts, and remove-time child unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fsl-mph-dr-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/isp116x-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/isp116x-hcd.c

## Purpose
`isp116x-hcd.c` is a USB 1.1 HCD for Philips/NXP ISP116x host controllers. It manages memory-mapped command/data register access, packs/unpacks ATL FIFO RAM transfer descriptors, schedules control/bulk/interrupt URBs, implements a two-port root hub interface, supports debugfs register dumps, and handles platform probe/remove and optional PM.

## Important APIs, Types, and Functions
- FIFO/PTD pipeline: `write_ptddata_to_fifo()`, `read_ptddata_from_fifo()`, `pack_fifo()`, `unpack_fifo()`, `preproc_atl_queue()`, `postproc_atl_queue()`, `start_atl_transfers()`, and `finish_atl_transfers()`.
- HCD operations: `isp116x_urb_enqueue()`, `isp116x_urb_dequeue()`, `isp116x_endpoint_disable()`, `isp116x_get_frame()`, `isp116x_reset()`, `isp116x_start()`, `isp116x_stop()`, `isp116x_bus_suspend()`, and `isp116x_bus_resume()`.
- IRQ/root hub: `isp116x_irq()`, `isp116x_hub_status_data()`, `isp116x_hub_control()`, `root_port_reset()`, and `isp116x_hub_descriptor()`.
- Platform/debug: `isp116x_probe()`, `isp116x_remove()`, debugfs show/create/remove helpers.

## Control Flow
Probe maps two 16-bit I/O resources for address and data, creates the HCD, initializes the async list and platform delay hooks, and calls `usb_add_hcd()`. Reset performs software reset and waits for clock-ready. Start validates chip ID, configures FIFO sizes, hardware interrupt polarity/triggering, root hub power/overcurrent policy, remote wakeup, frame interval, interrupt masks, operational state, and initially disables ports to avoid enumeration races.

URB enqueue rejects isochronous transfers, allocates endpoint state outside the spinlock, links the URB, initializes endpoint PID/toggle/maxpacket, schedules async endpoints on `async` or periodic interrupt endpoints in a balanced periodic tree, and starts ATL transfers. The scheduler builds an active endpoint chain for the current frame, respecting periodic load and async byte-time limits, then writes PTDs and payload into ATL FIFO. IRQ disables uP interrupts, acknowledges sources, finishes ATL FIFO when done, handles OHCI-like root hub events and unrecoverable errors, restarts transfers, and restores interrupt enable state. Completion analyzes PTD condition codes, handles short/control underruns, toggles, retries, zero packets, and calls `finish_request()` to give back URBs.

## State and Persistence Behavior
State lives in `struct isp116x`: register bases, platform data, interrupt masks, cached root hub descriptors/status, async list, periodic load/tree, frame index, active ATL chain, FIFO byte counters, and `atl_finishing`. Each endpoint stores PTD, PID state, error count, packet length/data pointer, periodic branch/load, and async list node. No disk persistence exists; debugfs exposes live register/state snapshots.

## Dependencies and Integration Points
The file depends on `isp116x.h` register/PTD definitions, Linux USB HCD APIs, platform data from `linux/usb/isp116x.h`, platform resources, debugfs, timers, PM, and platform-specific delay callbacks unless configured otherwise.

## Risks and Test Signals
Risks include lack of isochronous support, strict register access timing requirements, FIFO packing alignment/endian mistakes, active URB dequeue waiting for IRQ, periodic bandwidth accounting errors, reset timing quirks, and child devices requiring longer port resets. Test signals include usbtest 1-14 noted in comments, control/bulk/interrupt traffic at full/low speed, short packet and zero-packet behavior, periodic load saturation, root hub two-port feature requests, remote wakeup/suspend/resume, debugfs reads while running/suspended, and fault injection for chip ID, clock-ready timeout, IRQ, and resource mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/isp116x-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/isp116x.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/isp116x.h

## Purpose
`isp116x.h` is the private register, bitfield, data-structure, and access-helper header for the ISP116x HCD. It defines host-controller registers, root hub bits, FIFO/PTD format, condition-code error mapping, scheduler constants, controller/endpoint state, register I/O helpers, and optional tracing helpers.

## Important APIs, Types, and Functions
- Register definitions: OHCI-like `HC*` registers, uP interrupt registers, hardware config, DMA config, FIFO ports, buffer status, root hub descriptors/status/port bits.
- Transfer descriptor: packed `struct ptd` plus `PTD_GET_*` and `PTD_*` field macros.
- Status mapping: `cc_to_error[16]` maps PTD condition codes to Linux errno values.
- Runtime structures: `struct isp116x` and `struct isp116x_ep`.
- Access helpers: `isp116x_write_addr()`, `isp116x_write_data16()`, raw 16-bit helpers, 32-bit helpers, `isp116x_read_reg16/32()`, and `isp116x_write_reg16/32()`.

## Control Flow Role
The header underpins all execution in `isp116x-hcd.c`. PTD macros are used before packing FIFO contents and after unpacking hardware results. Register helpers enforce required delays after address/data accesses. Scheduler fields in `struct isp116x` connect async and periodic queue construction to the active FIFO batch.

## State and Persistence Behavior
`struct isp116x` stores controller-wide volatile state: locks, mapped registers, platform data, interrupt masks, cached root hub values, async and periodic schedules, current active FIFO batch, and finishing flag. `struct isp116x_ep` stores per-endpoint volatile state including current PTD, PID, error count, active chain link, periodic placement, and async schedule node.

## Dependencies and Integration Points
The header relies on Linux USB, errno, I/O accessors, debugfs/seq support through users in the C file, and platform delay callbacks controlled by `USE_PLATFORM_DELAY`. It expects platform data to provide timing behavior when platform delays are enabled.

## Risks and Test Signals
Risks include platform delay misconfiguration, endian-sensitive raw vs normal 16-bit FIFO access, packed/aligned PTD assumptions, bitfield macro correctness, and duplicated TD condition-code semantics with the C file. Test signals include compile coverage with/without trace macros and PM/debugfs, sparse/endian checks, PTD encode/decode round trips, register access timing on target hardware, and error-code mapping validation for every PTD condition code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/isp116x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/max3421-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/max3421-hcd.c

## Purpose
`max3421-hcd.c` is a USB host-controller driver for Maxim MAX3421E, a full-/low-speed USB host connected over SPI. Because SPI transactions can sleep, the driver serializes all chip I/O through a dedicated kernel thread and uses a spinlock-protected HCD state model for URB queues, root hub status, and endpoint metadata.

## Important APIs, Types, and Functions
- SPI I/O: `spi_rd8()`, `spi_wr8()`, `spi_rd_buf()`, and `spi_wr_buf()`.
- Transfer engine: `max3421_select_and_start_urb()`, `max3421_next_transfer()`, `max3421_ctrl_setup()`, `max3421_transfer_in()`, `max3421_transfer_out()`, `max3421_host_transfer_done()`, `max3421_recv_data_available()`, `max3421_handle_error()`, and `max3421_urb_done()`.
- Thread/IRQ/reset: `max3421_spi_thread()`, `max3421_irq_handler()`, `max3421_handle_irqs()`, `max3421_reset_hcd()`, and `max3421_reset_port()`.
- HCD/root hub/platform: `max3421_reset()`, `max3421_start()`, `max3421_urb_enqueue()`, `max3421_urb_dequeue()`, `max3421_endpoint_disable()`, `max3421_hub_status_data()`, `max3421_hub_control()`, `max3421_probe()`, and `max3421_remove()`.

## Control Flow
Probe validates SPI setup, IRQ, and platform/OF VBUS GPIO-output data, creates the HCD, allocates small DMA-safe SPI buffers, starts the SPI thread, registers the HCD, and requests the SPI IRQ. The thread configures PINCTL, waits for a supported chip revision, then loops: completes URBs, handles MAX3421 interrupts, selects new URBs when idle, and services todo bits for HCD reset, bus reset, unlink checks, and I/O-pin updates. The hard IRQ only wakes the thread and disables the IRQ until the thread is ready to sleep again.

The scheduler scans endpoint queues in periodic then non-periodic passes. It sets device address, speed/HUBPRE mode, packet state, and host-transfer command. Completion reads HRSL, handles errors or NAK/retry, reads IN FIFO data on RCVDAV, updates actual lengths, moves control transfers through setup/data/status, saves data toggles, unlinks the URB, and gives it back outside the spinlock.

Root hub control exposes one port, uses `port_status` lower 16 bits plus change bits in upper 16, powers VBUS through MAX3421 GPOUT pins, samples connection state from J/K bits, and performs reset through `HCTL.BUSRST`.

## State and Persistence Behavior
Runtime state is in `struct max3421_hcd`: SPI thread pointer, root hub state, port status/change mask, endpoint list, chip revision, frame number, current URB, scheduling pass, current packet length, interrupt-enable shadow, mode shadow, I/O pin shadows, todo bits, and optional debug counters. Per-endpoint state tracks packet state, retries, retransmit, NAK count, and last active frame. No persistent storage exists.

## Dependencies and Integration Points
The file integrates Linux SPI, USB HCD, OF/platform data (`maxim,vbus-en-pin`), kthreads, IRQs, and root hub polling (`HCD_FLAG_POLL_RH`). It maps MAX3421 register protocol and result codes into Linux USB core behavior.

## Risks and Test Signals
Risks include sleeping SPI operations accidentally called with locks held, endpoint disable freeing state while queued URBs remain, unsupported isochronous packet sizes above the 64-byte FIFO, NAK/retry behavior starving bulk endpoints, chip revision 0x12 retransmit workaround, incomplete bus suspend/resume returning `-1`, and remove not explicitly freeing tx/rx buffers after `usb_put_hcd()`. Test signals include SPI IRQ/thread wake behavior, attach/detach and low-speed detection, VBUS GPOUT polarity, control enumeration, bulk IN/OUT with zero packets, interrupt interval scheduling, NAK/error/retry injection, unlink of current and queued URBs, and OF/platform-data validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/max3421-hcd.c -->
