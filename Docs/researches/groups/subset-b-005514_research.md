# subset-b-005514 research

Grouped research for the xHCI debug capability, debugfs, extended capability, platform, hub, memory, and MediaTek scheduler files under `sources/distributed-fs/ceph-client/drivers/usb/host`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgcap.c -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgcap.c

Purpose: implements xHCI Debug Capability (DbC) device support. It discovers and owns the DbC MMIO register block, allocates the DbC event and bulk rings, builds the DbC context and USB string descriptors, exposes sysfs controls, polls the DbC event ring, and bridges successful configuration/disconnect events to a higher-level `dbc_driver` such as the tty backend.

Important APIs and functions: `xhci_create_dbc_dev()` finds `XHCI_EXT_CAPS_DEBUG` and probes the tty backend; `xhci_alloc_dbc()` initializes defaults and sysfs attributes; `xhci_dbc_remove()` tears down sysfs and hardware state; `dbc_alloc_request()`, `dbc_free_request()`, and `dbc_ep_queue()` are the backend-facing request API. Internal control centers are `xhci_dbc_mem_init()`, `xhci_do_dbc_start()`, `xhci_dbc_stop()`, `xhci_dbc_do_handle_events()`, and `dbc_handle_xfer_event()`. PM integration is via `xhci_dbc_suspend()` and `xhci_dbc_resume()`.

Control flow: enable starts from the `dbc` sysfs store path, takes a runtime PM reference, enables the hardware, allocates rings/ERST/context/string DMA memory, writes `DCCP`, `DEVINFO`, `ERSTBA`, and `ERDP`, then starts delayed event polling. The event worker advances `DS_DISABLED -> DS_INITIALIZED -> DS_ENABLED -> DS_CONNECTED -> DS_CONFIGURED`, calls `driver->configure()` on configuration, calls `driver->disconnect()` on unplug/reset, and reschedules itself at a fast poll interval when traffic is active. Transfers are queued by DMA mapping a `dbc_request`, writing one normal TRB, issuing a memory barrier before cycle-bit handoff, ringing the DbC doorbell, and placing the request on the endpoint pending list.

State and persistence: all state is volatile kernel/runtime hardware state in `struct xhci_dbc`. Persistent user-facing configuration exists only while the controller device exists: vendor/product/device IDs, protocol, strings, and poll interval are mutable through sysfs but only most identity/string fields require `DS_DISABLED`. Pending request state lives in `dbc_ep.list_pending`; hardware position lives in TRB rings and ERDP. `resume_required` remembers whether DbC should be restarted after system resume.

Dependencies and integration points: depends on core xHCI ring/context helpers, xHCI extended capability scanning, DMA coherent allocation, sysfs, runtime PM, workqueues, xHCI tracepoints, and `io-64-nonatomic-lo-hi` register writes. The tty layer consumes the request API and supplies `dbc_driver.configure/disconnect`. `xhci.c` calls create/remove and PM hooks during controller lifecycle.

Risks: event handling is lock-heavy and callbacks intentionally drop `dbc->lock`, so callback code must not assume hardware state remains stable. `dbc_ep_queue()` always schedules event work even when queueing failed. Ring accounting assumes one TRB per request (`WARN_ON(num_trbs != 1)`), making request size limits critical. STALL handling intentionally keeps some stalled requests queued to stay synchronized with hardware, which is subtle and prone to stale-request edge cases. `xhci_dbc_mem_cleanup()` frees several DMA allocations unconditionally after stop and depends on start/stop ordering to avoid NULL/free mismatches. Sysfs stores mutate registers directly and require accurate state gating.

Test signals: enable/disable through sysfs; configurable string/ID sysfs writes before enable; connection/configuration with a DbC host; bulk read/write completion and STALL/ClearFeature cases; cable unplug and port reset recovery; suspend/resume with `resume_required`; tracepoints `xhci_dbc_*`; runtime PM reference balance; fault injection for DMA allocation failure and queue-full return paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgcap.h -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgcap.h

Purpose: declares the xHCI DbC register layout, context/string/request data structures, constants, state machine values, endpoint helpers, and public DbC APIs used by `xhci-dbgcap.c` and `xhci-dbgtty.c`.

Important APIs and types: `struct dbc_regs` mirrors the DbC extended capability register block; `struct dbc_info_context` and descriptor/string structs describe the DMA context data written to DbC; `enum dbc_state` defines `DS_DISABLED` through `DS_CONFIGURED`; `struct dbc_ep`, `struct xhci_dbc`, `struct dbc_port`, and `struct dbc_request` are the core runtime objects. Public APIs include `xhci_create_dbc_dev()`, `xhci_remove_dbc_dev()`, `xhci_dbc_init/exit()`, `xhci_dbc_suspend/resume()`, `xhci_alloc_dbc()`, `xhci_dbc_remove()`, `dbc_alloc_request()`, `dbc_free_request()`, and `dbc_ep_queue()`.

Control flow: this header shapes the split between the hardware DbC engine and the tty backend. `struct dbc_driver` provides `configure()` and `disconnect()` callbacks invoked by the hardware layer. Endpoint helper macros map context byte offsets and ring enqueue DMA addresses for bulk IN/OUT. Conditional stubs compile DbC calls away when `CONFIG_USB_XHCI_DBGCAP` is disabled.

State and persistence: `struct xhci_dbc` centralizes volatile state: MMIO regs, rings, ERST, context, DMA string table, identity strings, state enum, delayed work, endpoints, backend driver, and backend private pointer. `struct dbc_port` stores tty-side pools, queues, kfifo-related state, minor number, tasklet, and registration flags. No persistent storage is defined.

Dependencies and integration points: includes Linux tty and kfifo support and depends on xHCI core types declared elsewhere. The header is included by the DbC hardware and tty sources and referenced from generic xHCI lifecycle code. Compile-time behavior depends on `CONFIG_USB_XHCI_DBGCAP` and `CONFIG_PM`.

Risks: layout definitions must match the xHCI DbC specification exactly; any incorrect offset or endian annotation corrupts hardware interaction. `DBC_CONTEXT_SIZE` and context-offset macros assume three 64-byte contexts. `dbc_ep_dma_direction()` encodes direction as a boolean convention, so inconsistent `BULK_IN/BULK_OUT` use would invert DMA mapping direction. Stubs return success when disabled, so call sites must not rely on side effects if DbC is not configured.

Test signals: build with DbC enabled/disabled; sparse/endian checking on `__le*` fields; structure offset validation against spec during review; tty backend compile coverage; PM-enabled and PM-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgtty.c -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgtty.c

Purpose: provides the tty backend for DbC, exposing a configured debug capability as dynamic raw serial devices named `ttyDBC*`. It maps tty writes into DbC bulk OUT requests and DbC bulk IN completions into tty flip-buffer input.

Important APIs and functions: global lifecycle uses `dbc_tty_init()` and `dbc_tty_exit()`. Device lifecycle uses `xhci_dbc_tty_probe()` and `xhci_dbc_tty_remove()`. The backend callbacks are `xhci_dbc_tty_register_device()` and `xhci_dbc_tty_unregister_device()` through `struct dbc_driver`. TTY operations include install/open/close/write/put_char/flush/write_room/chars_in_buffer/unthrottle. Request completions are `dbc_read_complete()` and `dbc_write_complete()`.

Control flow: `dbc_tty_init()` allocates a 64-minor dynamic tty driver. Probe allocates `dbc_port`, calls `xhci_alloc_dbc()`, stores `port` in `dbc->priv`, and assigns `xhci->dbc`. When DbC reaches configured state, the backend initializes a tty port, allocates an IDR minor, allocates the transmit kfifo and read/write request pools, then registers the tty device. On tty activation it queues read requests. Writes fill the kfifo, preserve each tty write as a transfer boundary with `tx_boundary`, and queue available write requests to DbC. Read completions push immediately to tty unless throttled or partially copied; otherwise they enqueue to `read_queue` and a tasklet retries.

State and persistence: state is runtime-only: global tty driver and IDR minor map; per-port kfifo, request pools, pending read queue, tasklet, lock, minor, and `registered/tx_running/tx_boundary` flags. Request buffers are owned by pool lists when idle and by DbC pending lists while in flight.

Dependencies and integration points: depends on `xhci-dbgcap.h` request APIs, tty core, tty flip buffers, IDR, kfifo, spinlocks, tasklets, and the xHCI device lifecycle. The tty backend is selected by `xhci_create_dbc_dev()` through `xhci_dbc_tty_probe()`.

Risks: concurrency spans tty methods, tasklet context, and DbC completion callbacks; `port_lock` protects list/kfifo state but completion callbacks drop into tty core paths. Partial flip-buffer copies rely on `n_read` and deferred retry ordering. `dbc_tty_write()` returns 0 while a previous write boundary is pending, which can affect user-space write behavior. Unregister must hang up and free all request pools without racing active completions; correctness depends on DbC stop/flush before request memory is freed.

Test signals: loading/unloading tty driver; minor allocation and reuse; opening/closing `ttyDBC0`; large writes split into 1024-byte requests while respecting write boundaries; throttled tty RX and unthrottle; cable disconnect causing `-ESHUTDOWN`; fault injection for partial request-pool allocation; lockdep for tty callbacks and tasklet paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgtty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-debugfs.c

Purpose: builds the xHCI debugfs hierarchy for controller registers, extended capabilities, command/event/endpoint rings, device contexts, port status/link information, stream selection, stream context arrays, and roothub bandwidth queries.

Important APIs and functions: `xhci_debugfs_create_root()`/`xhci_debugfs_remove_root()` manage the top-level `usb_debug_root/xhci` directory. Per-controller lifecycle is `xhci_debugfs_init()` and `xhci_debugfs_exit()`. Per-device and endpoint hooks are `xhci_debugfs_create_slot()`, `xhci_debugfs_remove_slot()`, `xhci_debugfs_create_endpoint()`, `xhci_debugfs_remove_endpoint()`, and `xhci_debugfs_create_stream_files()`. Internal helpers create regsets, ring files, context files, ports, and bandwidth views.

Control flow: controller init creates a directory named after the controller device, attaches regset32 files for capability/operational/runtime and selected extended capability registers, creates command and event ring directories, a devices directory, per-port `portsc`/`portli` files, and bandwidth files. Device allocation creates a slot directory with EP0 ring and context files; endpoint configuration adds per-endpoint ring directories; stream setup adds stream selector and stream context dump files. Exit removes debugfs recursively, then frees the regset metadata list.

State and persistence: debugfs state is volatile. `xhci->debugfs_root`, `xhci->debugfs_slots`, per-device `debugfs_private`, per-endpoint `xhci_ep_priv`, and the `regset_list` hold metadata and live pointers into xHCI rings/contexts. No persistent configuration exists, except debugfs writes can trigger actions: `portsc` accepts `compliance`, and `stream_id` selects which stream ring a debugfs endpoint directory shows.

Dependencies and integration points: depends on Linux debugfs, seq_file, uaccess, xHCI decode helpers, xHCI port helpers, runtime PM for bandwidth query, and endpoint/device lifecycle calls from `xhci.c` and `xhci-mem.c`. Extended capability scanning uses `xhci_find_next_ext_cap()`.

Risks: most files dereference live xHCI pointers with minimal locking; correctness relies on debugfs teardown ordering and device/endpoint removal hooks. `bw_context_open()` assumes file names match one of the static maps. The `portsc` write path can put a port into compliance mode and must obey link-state and CTC constraints. `stream_id` changes `show_ring` based on user input and must reject stream 0/out-of-range IDs. Bandwidth files resume the controller with runtime PM, so PM error handling matters.

Test signals: debugfs tree presence after controller init; register dumps for legacy/protocol/DbC capabilities; ring TRB dumps before and after endpoint creation; endpoint removal while files are open; writing `compliance` only from RxDetect; stream ring switching; bandwidth query behavior across SS/HS/FS and runtime PM suspended controllers; debugfs-disabled build stubs from the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-debugfs.h

Purpose: declares debugfs register offsets, helper data structures, and exported debugfs lifecycle hooks for xHCI.

Important APIs and types: offset macros describe capability, operational, runtime, legacy-support, protocol, and DbC extended capability registers. `dump_register()` creates `debugfs_reg32` entries. `struct xhci_regset` tracks dynamically allocated regset metadata in `xhci->regset_list`; `struct xhci_file_map` maps debugfs filenames to seq show functions; `struct xhci_ep_priv` and `struct xhci_slot_priv` hold per-endpoint/per-slot debugfs metadata and live xHCI pointers. Public functions cover root/controller/device/endpoint/stream debugfs creation and removal.

Control flow: with `CONFIG_DEBUG_FS`, `xhci.c`, device allocation, endpoint configuration, and stream setup call the declared functions to maintain the debugfs tree. Without debugfs, inline stubs preserve call-site simplicity and compile out all side effects.

State and persistence: structures store debugfs-only runtime metadata. The header itself persists no data; it defines names, fixed maximum debugfs name length, and live pointer containers used by `xhci-debugfs.c`.

Dependencies and integration points: depends on Linux debugfs and xHCI core types. It is included by `xhci-debugfs.c` and by xHCI memory/lifecycle code that needs conditional calls.

Risks: register offset macros must remain synchronized with xHCI layout and the C source arrays. Per-slot `eps[31]` assumes xHCI endpoint index bounds. Stub functions silently do nothing, so debug-only diagnostics must not be required for functional behavior.

Test signals: `CONFIG_DEBUG_FS=y/n` builds; compile coverage for every declared function; debugfs path creation/removal in controller and endpoint lifecycle; review of offsets against xHCI spec and `xhci.h` register definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ext-caps.c -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ext-caps.c

Purpose: handles vendor-specific xHCI extended capabilities at controller initialization. In this file, the implemented behavior is Intel USB role-switch companion device creation for controllers advertising a vendor capability and the matching quirk.

Important APIs and functions: `xhci_ext_cap_init()` walks all extended capabilities with `xhci_find_next_ext_cap()`. `xhci_create_intel_xhci_sw_pdev()` creates an `intel_xhci_usb_sw` platform device with a memory resource mapped onto the vendor capability window. `xhci_intel_unregister_pdev()` is registered as a devm cleanup action. Cherryview additionally gets a managed software node property `sw_switch_disable`.

Control flow: init begins at the first extended capability, loops through each capability, reads the capability ID, and on Intel vendor capability checks `XHCI_INTEL_USB_ROLE_SW`. If set, it allocates the platform device, adds a 0x400-byte MMIO resource, optionally installs software node properties, parents it to the xHCI PCI device, registers it, and attaches a devm unregister action to the controller device.

State and persistence: no long-lived private state is kept in this file. The child platform device and its resource persist until the parent device is removed or devm cleanup runs.

Dependencies and integration points: depends on PCI device identity, platform device APIs, property/software-node APIs, xHCI quirk flags, and extended capability parsing from `xhci-ext-caps.h`. Exported `xhci_ext_cap_init()` is called by core xHCI initialization and exported GPL for host glue.

Risks: assumes the controller device is PCI when the Intel role switch quirk is active (`to_pci_dev(dev)`). Resource sizing is fixed at 0x400 bytes and must match the companion driver expectation. Returning an error aborts init on role-switch pdev failures, so device-property or platform registration regressions can block host setup for affected hardware.

Test signals: Intel role-switch hardware or emulated capability; Cherryview property attachment; failure paths for platform allocation/resource/property/add/devm action; non-Intel or no-quirk controllers should no-op; verify companion driver binds to `intel_xhci_usb_sw`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ext-caps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ext-caps.h -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ext-caps.h

Purpose: defines generic xHCI capability, command/status, and extended capability constants plus the inline scanner used throughout xHCI to traverse extended capability lists.

Important APIs and types: macros decode capability length, HCC extended capability pointer, extended capability ID/NEXT/VALUE, protocol port fields, PSI fields, legacy ownership bits, L1/HLC/BLC flags, Intel vendor IDs, Intel SPR tunnel detection offsets, command/status bits, and IRQ masks. `struct xhci_protocol_caps` reflects the supported protocol capability header. `xhci_find_next_ext_cap()` is the key inline API.

Control flow: `xhci_find_next_ext_cap(base, start, id)` starts from HCCPARAMS when `start` is 0 or the HCCPARAMS offset, converts xECP dword offsets to byte offsets, follows each NEXT pointer, skips the start capability itself on subsequent searches, and returns the next matching offset or the next capability for `id == 0`. It stops on missing lists, NEXT zero, or all-ones MMIO reads.

State and persistence: no runtime state. The scanner reads MMIO and returns byte offsets into the controller capability space.

Dependencies and integration points: includes `linux/io.h` for `readl()`. Used by debugfs, DbC discovery, role-switch vendor capability handling, roothub port-array setup, and Intel USB4 tunnel detection.

Risks: malformed hardware capability chains can still cause repeated or out-of-range offsets; `XHCI_MAX_EXT_CAPS` is defined but this inline scanner does not enforce an iteration bound. Callers must treat offset 0 as not found and must add offsets to the correct MMIO base. All-ones reads are treated as device removal/dead hardware.

Test signals: controllers with no ext caps; multiple protocol caps; repeated calls with previous offset; `id == 0` enumeration; hot-removal/all-ones MMIO behavior; malformed NEXT pointer review in fuzzed/emulated hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ext-caps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-histb.c -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-histb.c

Purpose: platform xHCI host driver for HiSilicon STB SoCs. It wraps the generic xHCI driver with SoC-specific MMIO configuration, clock/reset control, DMA mask setup, dual-HCD registration, and system sleep handling.

Important APIs and functions: `xhci_histb_probe()` and `xhci_histb_remove()` implement platform lifecycle. `xhci_histb_config()` programs USB2/USB3 PHY-related registers and threshold registers. `xhci_histb_clks_get()`, `xhci_histb_host_enable()`, and `xhci_histb_host_disable()` manage clock/reset sequencing. `xhci_histb_setup()` is a generic xHCI reset override. PM hooks are `xhci_histb_suspend()` and `xhci_histb_resume()`. Module entry/exit register the platform driver after `xhci_init_driver()`.

Control flow: probe checks `usb_disabled()`, allocates private state, fetches IRQ and MMIO resource, gets required clocks and soft reset, enables runtime PM, sets a 32-bit DMA mask, creates the primary HCD, enables clocks/resets, obtains `xhci`, creates the shared USB3 HCD, applies DT property quirks, registers USB2 then USB3 HCDs, and forbids runtime PM by default. Remove reverses HCD registration, disables wakeup, clocks, reset, and runtime PM. Suspend delegates to generic `xhci_suspend()` and disables host resources when wakeup is not allowed; resume re-enables resources then calls `xhci_resume()`.

State and persistence: `struct xhci_hcd_histb` is driver data attached to the controller device and owns MMIO, clocks, reset, and primary HCD pointer. Hardware register programming persists until reset/power loss; software state is runtime-only.

Dependencies and integration points: depends on platform device resources, OF matching (`hisilicon,hi3798cv200-xhci`), common clock framework, reset controller, PM runtime, USB HCD core, and generic xHCI setup/resume/suspend.

Risks: clock enable error unwinding must keep exact reverse order. `reset_control_deassert()` return is not checked, so reset-controller failures may be missed. Probe calls `pm_runtime_get_sync()` without checking a negative return. Register constants are SoC-specific and can be wrong for close variants. Runtime PM is enabled but then forbidden after probe, so power expectations should be explicit in board integration.

Test signals: probe/remove on matching DT; missing clock/reset/property failure paths; USB2/USB3 enumeration; DT properties `usb2-lpm-disable`, `usb3-lpm-capable`, and `imod-interval-ns`; system suspend/resume with and without wakeup enabled; DMA mask failure path on constrained platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-histb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-hub.c -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-hub.c

Purpose: implements xHCI roothub behavior. It synthesizes USB2/USB3 hub and BOS descriptors, translates hub class requests into PORTSC/PORTPMSC operations, reports port changes, manages port power/link/reset/test state, tracks suspend/resume state, and handles several controller quirks.

Important APIs and functions: exported functions include `xhci_port_state_to_neutral()`, `xhci_hub_control()`, `xhci_hub_status_data()`, and under PM `xhci_bus_suspend()`, `xhci_bus_resume()`, `xhci_get_resuming_ports()`. Helpers include BOS descriptor creation, hub descriptor builders, `xhci_stop_device()`, `xhci_ring_device()`, `xhci_set_port_power()`, `xhci_enter_test_mode()`, `xhci_exit_test_mode()`, `xhci_port_is_tunneled()`, `xhci_set_link_state()`, and status translators for USB2/USB3 ports.

Control flow: `xhci_hub_control()` handles hub requests under `xhci->lock`: descriptor reads, BOS reads for USB3+, port status reads, feature sets, and feature clears. Port status conversion combines raw PORTSC status/change bits with driver state such as `suspended_ports`, `resuming_ports`, `port_c_suspend`, and resume timestamps. Suspend paths first validate every port, prepare neutral PORTSC writes, stop endpoints for ports being suspended, then write U3/wake state. Resume writes links toward U0/RESUME, optionally disables the primary interrupter for USB2 resume, waits for PLC, clears PLC, and rings device doorbells.

State and persistence: roothub state is in `struct xhci_hub` and `struct xhci_bus_state`: per-port pointers, port counts, suspended/resuming bitmaps, remote wake flags, `port_c_suspend`, and next state-change deadlines. Per-port state includes slot IDs, resume timestamps, rexit/u3exit completions, and hardware PORTSC/PORTPMSC registers. Test mode state is `xhci->test_mode`.

Dependencies and integration points: depends on USB core hub request definitions, xHCI command queue for stop endpoint and slot disable, xHCI port register helpers, ACPI port power helpers, runtime PM policy, PCI vendor checks for Intel tunnel detection, tracepoints, and quirk flags. Used through `hc_driver.hub_control`, `hub_status_data`, and PM bus hooks.

Risks: PORTSC has mixed RO/RWS/RW1C semantics, so every write must be neutralized correctly or changes can be lost/spurious. Several paths drop and reacquire `xhci->lock` while sleeping or issuing commands; port state can change in between. BOS SSP descriptor generation depends on protocol PSI parsing and contains compatibility fixes for ambiguous Gen1x2/Gen2x1 entries. Resume timing is subtle and includes synthetic status to keep usbcore polling. Test mode disables slots and power and resets the controller on exit, so it is high-impact. `xhci_stop_device()` allocates commands while under lock with partial unwind complexity.

Test signals: hub descriptor and BOS descriptor contents for USB2, USB3.0, USB3.1/3.2 with and without PSI; Set/ClearPortFeature for power/reset/suspend/link/U1/U2/test/compliance; port change bit clearing; USB2 and USB3 suspend/resume including remote wake; over-current bailout; compliance-mode quirk and missing-CAS quirk; Intel tunnel detection; disconnect during resume; all-ones PORTSC removal handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mem.c -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mem.c

Purpose: owns xHCI memory allocation, initialization, and cleanup for DMA-visible structures: TRB rings and segments, device/input contexts, stream contexts, virtual devices, endpoint contexts, scratchpads, interrupters/ERSTs, root-hub port arrays, and bandwidth accounting tables.

Important APIs and functions: ring APIs are `xhci_ring_alloc()`, `xhci_ring_init()`, `xhci_ring_free()`, `xhci_ring_expansion()`, and `xhci_dma_to_transfer_ring()`. Context APIs include `xhci_alloc_container_ctx()`, `xhci_get_input_control_ctx()`, `xhci_get_slot_ctx()`, and `xhci_get_ep_ctx()`. Device/endpoint APIs include `xhci_alloc_virt_device()`, `xhci_free_virt_device()`, `xhci_setup_addressable_virt_dev()`, `xhci_endpoint_init()`, `xhci_endpoint_zero()`, bandwidth update/copy helpers, stream allocation/free, command allocation/free, secondary interrupter create/remove, `xhci_mem_init()`, and `xhci_mem_cleanup()`.

Control flow: controller init allocates DCBAA, DMA pools, command ring, primary interrupter/event ring/ERST, scratchpads, and roothub port arrays derived from protocol extended capabilities. Device allocation creates input/output contexts, initializes 31 virtual endpoints, allocates EP0 ring, and writes the DCBAA slot pointer. Endpoint init parses endpoint descriptors into xHCI interval/mult/burst/type/max payload fields, allocates a new ring, and fills the endpoint context. Stream allocation builds a stream context array, allocates one ring per usable stream, and maintains a radix tree from TRB DMA segment keys to stream rings. Cleanup reverses controller resources, recursively frees virtual devices depth-first, removes debugfs slots, destroys DMA pools, and clears topology/bandwidth state.

State and persistence: all state is runtime kernel/hardware state. Persistent hardware-visible state is represented by DMA memory referenced by controller registers and DCBAA entries. Software tracks ring enqueue/dequeue/cycle/free counts, stream radix mappings, virtual devices in `xhci->devs`, roothub port topology in `xhci->hw_ports`, `usb2_rhub`, `usb3_rhub`, port capability cache in `xhci->port_caps`, and bandwidth tables in `xhci->rh_bw`.

Dependencies and integration points: depends on DMA pools/coherent allocation, radix trees, xHCI register/capability helpers, debugfs slot removal, tracepoints, USB endpoint descriptors, TT bandwidth accounting, and host quirks. Generic xHCI initialization and enumeration call these routines heavily; platform drivers depend on `xhci_mem_init()` during setup.

Risks: allocation failure unwind is broad and must tolerate partially initialized fields; `xhci_mem_init()` maps all failures to `-ENOMEM` even when port-cap setup returns `-ENODEV`. Ring expansion must preserve cycle state and stream DMA mappings. Stream context counts must remain power-of-two-compatible and reserve command TRBs. Device teardown must clear DCBAA and roothub slot IDs to avoid hardware or software stale references. Protocol-cap parsing has duplicate-port and vendor quirk handling; wrong port maps break roothubs and bandwidth domains. Several helper comments document known limitations, such as EP0 dequeue tracking after Set TR Dequeue Pointer.

Test signals: controller init/cleanup under allocation fault injection; ring allocation/free/expansion and TRB link toggles; stream allocation with many stream counts and DMA-to-ring lookup; virtual device allocation/free and depth-first hub TT cleanup; endpoint context values across speeds and transfer types; scratchpad allocation for controllers with nonzero scratchpads; secondary interrupter create/remove; protocol capability parsing with duplicate/unknown ports and PSI entries; debugfs slot removal during device free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk-sch.c -->
## sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk-sch.c

Purpose: implements MediaTek-specific periodic endpoint bandwidth scheduling for xHCI. It computes microframe offsets, split transaction placement, and reserved endpoint context fields required by MediaTek hardware for interrupt/isochronous endpoints, especially FS/LS devices behind transaction translators.

Important APIs and functions: public hooks are `xhci_mtk_sch_init()`, `xhci_mtk_sch_exit()`, `xhci_mtk_add_ep()`, `xhci_mtk_drop_ep()`, `xhci_mtk_check_bandwidth()`, and `xhci_mtk_reset_bandwidth()`. Core helpers include `get_bw_info()`, `find_tt()`, `drop_tt()`, `create_sch_ep()`, `setup_sch_info()`, `check_sch_bw()`, `alloc_sch_microframes()`, `alloc_sch_portion_of_frame()`, `check_sch_tt_budget()`, `update_sch_tt()`, and `update_bus_bw()`.

Control flow: scheduler init allocates one bandwidth domain per USB2 root port plus separate IN/OUT domains per USB3 root port. Endpoint add first delegates to generic `xhci_add_endpoint()`, then for periodic endpoints needing MediaTek scheduling creates a `mu3h_sch_ep_info`, calculates packet/budget tables from the xHCI endpoint context, queues it on `bw_ep_chk_list`, and hashes it by endpoint pointer. `xhci_mtk_check_bandwidth()` walks pending endpoints, finds a valid offset under bus and TT constraints, writes MediaTek fields (`BPKTS`, `BCSCOUNT`, `BBM`, `BOFFSET`, `BREPEAT`) into reserved endpoint context dwords, then delegates to generic `xhci_check_bandwidth()`. Reset destroys pending scheduler endpoints and calls generic reset.

State and persistence: `mtk->sch_array` stores per-domain bandwidth arrays. `mtk->bw_ep_chk_list` contains endpoints pending bandwidth check for the current configuration transaction. `mtk->sch_ep_hash` maps USB endpoint pointers to scheduler state for drop. For FS/LS behind TTs, `usb_tt.hcpriv` stores `mu3h_sch_tt` structures or per-port pointer arrays, with bus/frame bandwidth arrays and IN start-split counts. Scheduled endpoints maintain allocated offsets and budget tables until dropped/reset.

Dependencies and integration points: depends on generic xHCI endpoint add/drop/check/reset, xHCI endpoint context encoding, MediaTek definitions from `xhci-mtk.h`, USB TT structures, endpoint descriptors, and xHCI roothub port mapping created by memory init. It is wired into `xhci-mtk.c` through xHCI driver overrides.

Risks: scheduling is combinatorial and sensitive to USB split-transaction rules: Start-Split cannot be in Y6, Complete-Split must not overflow microframe 7, FS/LS per-microframe and per-frame limits must hold, and IN/OUT split overlap rules avoid downstream errors. `usb_tt.hcpriv` sharing must be correct for single-TT and multi-TT hubs. Failure after some endpoints are marked allocated can leave bandwidth loaded until reset if unwind is incomplete. Endpoint pointer hashing assumes stable endpoint objects. Reserved endpoint-context fields are MediaTek-specific and must not leak to non-MTK hosts.

Test signals: periodic endpoint add/drop for HS/SS/SSP and FS/LS behind single- and multi-TT hubs; bandwidth exhaustion returning `-ENOSPC`; split transaction edge cases around Y6/Y7 and frame crossing; isoc IN/OUT overlap scenarios; reset bandwidth after failed configuration; context reserved field values matching expected BPKTS/CSCOUNT/BM/OFFSET/REPEAT; generic xHCI bandwidth still called after MediaTek scheduling succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk-sch.c -->
