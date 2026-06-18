# subset-b-005488 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/gadget.c

Purpose: implements the DesignWare USB3 device-side gadget binding for the Linux USB gadget framework. It owns gadget endpoint setup, request queueing, TRB preparation, endpoint commands, run/stop pullup handling, device events, endpoint events, runtime PM interactions, and UDC registration.

Important APIs/functions: external entry points include `dwc3_gadget_init`, `dwc3_gadget_exit`, `dwc3_gadget_suspend`, `dwc3_gadget_resume`, `dwc3_gadget_set_test_mode`, `dwc3_gadget_get_link_state`, `dwc3_gadget_set_link_state`, `dwc3_gadget_start_config`, `dwc3_send_gadget_generic_command`, `dwc3_send_gadget_ep_cmd`, `dwc3_remove_requests`, `dwc3_stop_active_transfer`, and `dwc3_gadget_giveback`. The gadget-facing ops table exports endpoint operations (`enable`, `disable`, request allocation/free, `queue`, `dequeue`, halt/wedge) and gadget operations (`pullup`, `udc_start`, `udc_stop`, speed selection, wakeup, VBUS draw, config checks). Core internal state pivots on `struct dwc3`, `struct dwc3_ep`, `struct dwc3_request`, `struct dwc3_trb`, and `struct dwc3_event_buffer`.

Control flow: `dwc3_gadget_init` allocates EP0 TRBs, setup and bounce buffers, a `usb_gadget`, endpoint objects, and registers the gadget. Binding a gadget driver via `dwc3_gadget_start` requests the gadget IRQ and records the driver. Pullup connect runs a soft reset, installs event buffers, starts EP0 OUT setup reception, enables device events, sets speed, and sets `DCTL.RUN_STOP`; pullup disconnect stops active transfers, waits or forces EP0 back to setup phase, clears run/stop, disables EP0, and marks the gadget not attached. Request queueing maps DMA, moves requests from `pending_list` to `started_list`, builds TRBs, and issues `STARTTRANSFER` or `UPDATETRANSFER`; completions reclaim TRBs, update actual length/status, give requests back outside the spinlock, and continue queued work. Interrupt top half snapshots the hardware event buffer and masks it, while the threaded handler processes endpoint and device events under `dwc->lock`.

State and persistence: state is entirely in kernel memory and device registers. Endpoint state is tracked with flags such as `DWC3_EP_ENABLED`, `TRANSFER_STARTED`, `END_TRANSFER_PENDING`, `DELAY_START`, `DELAY_STOP`, `STALL`, stream flags, and FIFO allocation flags. Request state spans pending/started/cancelled lists and `DWC3_REQUEST_STATUS_*`. Controller state tracks `connected`, `softconnect`, `pullups_connected`, `suspended`, `ep0state`, wakeup configuration, setup pending, TX FIFO resizing counters, event buffer positions, and speed. DMA-coherent TRB/bounce/setup resources persist until gadget exit.

Dependencies and integration: depends on DWC3 core register definitions, debug helpers, EP0 logic in the same driver family, Linux USB gadget/UDC APIs, DMA mapping, platform IRQ resources, PM runtime, workqueues, tracepoints, USB PHY/power supply hooks, and hardware version macros for numerous Synopsys workarounds. It integrates with xHCI/DRD role switching through `dwc3_core_soft_reset`, `dwc3_set_prtcap` users, event buffer setup, SUSPHY control, and exported gadget init/exit functions used by the core or glue layer.

Risks: high concurrency and hardware ordering sensitivity. TRB HWO updates require memory barriers, command completion is timeout based, and End Transfer has delayed-stop paths when EP0 setup/status phases can block endpoint commands. Disconnect, reset, halt clearing, stream restart, and isochronous scheduling all have controller-revision-specific behavior. FIFO resizing can fail if RAM depth is overcommitted. Incorrect event count handling can drop events. Runtime PM paths must avoid duplicate run/stop sequences. Remote wakeup and function wakeup require link-state and arming checks. DMA unmap/giveback must not occur before hardware has stopped using TRBs.

Test signals: meaningful coverage comes from USB gadget enumeration at FS/HS/SS/SSP, configfs/composite functions, mass-storage and networking functions, EP halt/wedge tests, request dequeue during traffic, disconnect/reset storms, suspend/resume and remote wakeup, isochronous audio/video, bulk streams, scatter-gather I/O, runtime PM role switching, and tracing via `trace_dwc3_*` events. Regression indicators include command timeout logs, invalid event count logs, request status mismatches, missed isoc frames, stale pending requests, and enumeration failures after BOS/LPM negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/gadget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/gadget.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/gadget.h

Purpose: declares DWC3 gadget-side constants, endpoint/request conversion helpers, request-list helpers, and cross-file gadget APIs used by gadget, EP0, and core code.

Important APIs/types/functions: defines DEPCFG/DEPXFERCFG bit builders, U1/U2 latency defaults, `DWC3_FRNUMBER_MASK`, `to_dwc3_ep`, `to_dwc3_request`, `gadget_to_dwc`, `next_request`, `dwc3_gadget_move_started_request`, `dwc3_gadget_move_cancelled_request`, `dwc3_gadget_ep_get_transfer_index`, and `dwc3_gadget_dctl_write_safe`. It declares EP0 helpers, request giveback, halt setting, delayed status, active transfer stop, and start-config entry points.

Control flow: inline helpers are used in the request lifecycle. Queued requests are moved to `started_list` when TRBs are prepared and to `cancelled_list` when dequeue, stall clearing, disconnect, or transfer errors require later cleanup. `dwc3_gadget_ep_get_transfer_index` reads `DEPCMD` after `STARTTRANSFER`; `dwc3_gadget_dctl_write_safe` preserves link-state request bits during DCTL read-modify-write operations.

State and persistence: this header does not allocate state, but it defines how list membership and request status values are updated. Its bit macros encode persistent hardware register state in endpoint configuration commands and device control writes.

Dependencies and integration: includes Linux list and USB gadget headers plus `io.h`; depends on `core.h` types through included IO helpers. It is the local contract between `gadget.c`, `ep0.c`, and any DWC3 code that issues endpoint commands or manipulates gadget request lists.

Risks: these helpers assume callers hold the DWC3 lock. Misusing the move helpers can corrupt endpoint request lists. `dwc3_gadget_dctl_write_safe` is important because accidental nonzero `ULSTCHNGREQ` writes can request a link transition. The DEPCFG macros are low-level register encodings, so off-by-one endpoint numbers, FIFO numbers, burst sizes, or interval values lead to hardware misconfiguration.

Test signals: compile coverage is the main direct signal. Runtime validation appears through successful endpoint configuration, EP0 control traffic, stalled endpoint recovery, transfer-resource allocation, and absence of unexpected link-state changes during DCTL writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/gadget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/glue.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/glue.h

Purpose: defines the public interface used by platform glue drivers to probe, remove, suspend/resume, and optionally sequence DWC3 core, host, gadget, PHY suspend, and port-capability setup themselves.

Important APIs/types/functions: `struct dwc3_properties` carries software-managed core properties such as `gsbuscfg0_reqinfo` and `needs_full_reinit`; `DWC3_DEFAULT_PROPERTIES` supplies defaults. `struct dwc3_probe_data` packages a DWC3 context, MMIO resource, clock/reset ignore flags, `skip_core_init_mode`, and properties for `dwc3_core_probe`. The header declares `dwc3_core_probe/remove`, runtime/system PM callbacks, `dwc3_core_init/exit`, `dwc3_host_init/exit`, `dwc3_gadget_init/exit`, `dwc3_enable_susphy`, and `dwc3_set_prtcap`.

Control flow: normal glue drivers call `dwc3_core_probe` and let the core initialize the selected role. Glue drivers using `skip_core_init_mode` must explicitly call `dwc3_core_init`, select a port capability with `dwc3_set_prtcap`, initialize exactly one role with host or gadget init, then unwind in reverse order.

State and persistence: the header does not own state, but its structs control persistent core initialization choices and role-transition state stored in `struct dwc3`, including current role and low-power PHY settings.

Dependencies and integration: includes `core.h` and Linux types. It is consumed by platform-specific DWC3 wrappers that manage clocks, resets, power domains, USB role switches, and SoC-specific mode sequencing outside generic core code.

Risks: misuse of `skip_core_init_mode` can initialize host/gadget before the core is ready, initialize both roles simultaneously, or leave SUSPHY/PRTCAP inconsistent during role switches. The comment says "finial" but the semantics are clear. Glue drivers that ignore clocks/resets must fully own those resources.

Test signals: platform probe/remove tests, runtime PM cycling, system suspend/resume, role-switch transitions, and wakeup-capable platforms validate this contract. Failures show as missing xHCI/gadget registration, bad role mode, PHY suspend problems, or resource leaks on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/glue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/host.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/host.c

Purpose: creates and tears down the child `xhci-hcd` platform device used when a DWC3 controller operates in host mode.

Important APIs/functions: `dwc3_host_init` and `dwc3_host_exit` are exported. Helpers include `dwc3_power_off_all_roothub_ports`, `dwc3_xhci_plat_start`, `dwc3_host_fill_xhci_irq_res`, and `dwc3_host_get_irq`. A small `xhci_plat_priv` hook enables SUSPHY when the primary HCD starts.

Control flow: host init first temporarily maps the xHCI MMIO range and clears `PORT_POWER` for every root-hub port to avoid VBUS glitches. It resolves the IRQ by named resources (`host`, `dwc_usb3`) or index 0, allocates an `xhci-hcd` platform device, attaches DWC3 xHCI resources, adds software-node quirks and capability properties, passes platform private data, registers the child, and propagates wakeup settings. Exit disables child wakeup, enables SUSPHY, unregisters xHCI, and clears `dwc->xhci`.

State and persistence: persistent state is `dwc->xhci`, populated xHCI resource entries, wakeup configuration, and transient root-hub port power state. Software-node properties persist with the child device.

Dependencies and integration: depends on Linux platform devices, IRQ helpers, OF naming, USB HCD APIs, xHCI platform private data, xHCI register definitions, and DWC3 core resources. The child xHCI driver owns actual host operation after registration.

Risks: temporary MMIO mapping must match resource flags, and blindly powering off ports can surprise platforms if called at the wrong point. IRQ lookup fallback must not mask probe deferral. Property array size must match optional property count. Host exit assumes `dwc->xhci` is valid. Wakeup propagation matters when switching from gadget mode.

Test signals: successful xHCI child probe, root-hub enumeration, role switch from gadget to host, wakeup enable propagation, and absence of VBUS glitches on affected boards. Failures include IRQ probe deferral, xHCI registration errors, powered-off ports not recovering, or suspend/resume regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/io.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/io.h

Purpose: provides DWC3 register read/write helpers that compensate for the driver's MMIO mapping starting at the global register window while callers use Synopsys-documented xHCI-relative offsets.

Important APIs/functions: `dwc3_readl(struct dwc3 *dwc, u32 offset)` and `dwc3_writel(struct dwc3 *dwc, u32 offset, u32 value)`.

Control flow: both helpers derive `base` from `dwc->regs`, access `base + offset - DWC3_GLOBALS_REGS_START`, then emit tracepoints using a documentation-style base address (`base - DWC3_GLOBALS_REGS_START`) and the original offset.

State and persistence: no independent state. Reads and writes directly affect memory-mapped DWC3 hardware registers and trace output.

Dependencies and integration: includes Linux IO primitives, trace support, debug helpers, and core register constants. Nearly every DWC3 core, gadget, host-adjacent, and PHY helper depends on these accessors for consistent offset handling and traceability.

Risks: callers must pass offsets in the expected DWC3 register namespace; passing already-adjusted offsets would access the wrong register. Tracepoints expose all register access and can be high volume. No barriers beyond `readl`/`writel` semantics are added here, so call sites still need explicit ordering around DMA-visible structures.

Test signals: successful register access during probe, trace events with expected addresses, and absence of faults from invalid MMIO offsets. Low-level failures usually manifest as probe timeouts, command timeouts, or incorrect hardware capability reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/trace.c

Purpose: instantiates the DWC3 tracepoint definitions declared in `trace.h`.

Important APIs/functions: defines `CREATE_TRACE_POINTS` before including `trace.h`; this is the standard Linux tracepoint pattern that causes storage and registration code to be generated once.

Control flow: there is no runtime control flow in this file beyond compile-time tracepoint instantiation.

State and persistence: tracepoint static data generated by the tracing framework is linked into the module/kernel. It does not own device state.

Dependencies and integration: depends entirely on `trace.h` and the Linux trace event infrastructure. All `trace_dwc3_*` call sites in IO, gadget, and related DWC3 code rely on this translation unit existing exactly once.

Risks: defining tracepoints in more than one C file would cause duplicate symbol/link errors; omitting this file would leave tracepoint call sites unresolved. Trace ABI format changes affect tooling that parses DWC3 trace events.

Test signals: kernel/module build success and availability of DWC3 events under tracing (`events/dwc3/*`). Runtime enabling of DWC3 tracepoints should show register access, commands, requests, TRBs, and events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/trace.h

Purpose: declares the DWC3 trace event classes and concrete events used to inspect role changes, register IO, raw events, control requests, USB requests, gadget commands, endpoint commands, TRBs, and endpoint state.

Important APIs/types/functions: event classes include `dwc3_log_set_prtcap`, `dwc3_log_io`, `dwc3_log_event`, `dwc3_log_ctrl`, `dwc3_log_request`, `dwc3_log_generic_cmd`, `dwc3_log_gadget_ep_cmd`, `dwc3_log_trb`, and `dwc3_log_ep`. Concrete events include `dwc3_set_prtcap`, `dwc3_readl`, `dwc3_writel`, `dwc3_event`, `dwc3_ctrl_req`, `dwc3_alloc_request`, `dwc3_free_request`, `dwc3_ep_queue`, `dwc3_ep_dequeue`, `dwc3_gadget_giveback`, `dwc3_gadget_generic_cmd`, `dwc3_gadget_ep_cmd`, `dwc3_prepare_trb`, `dwc3_complete_trb`, `dwc3_gadget_ep_enable`, and `dwc3_gadget_ep_disable`.

Control flow: each trace call snapshots selected fields into trace ring buffers using `TP_fast_assign`, then formats them with helper decoders from `debug.h` and USB helper decoders. The header ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` integration.

State and persistence: trace entries are transient tracing data, but the event formats form a user-visible diagnostics contract. Captured fields include base address, endpoint name, request pointers, lengths/status, command parameters/status, TRB ring indices, flags, direction, and raw event words.

Dependencies and integration: depends on Linux tracepoint macros, byteorder helpers, `core.h`, and `debug.h`. It is included by normal source files for declarations and by `trace.c` with `CREATE_TRACE_POINTS` for definitions.

Risks: trace format strings dereference DWC3, endpoint, request, and TRB fields, so trace calls must pass live objects. Verbose register IO tracing can be expensive. Format changes can break scripts. Pointer printing and base addresses are useful for debugging but require normal kernel tracing access controls.

Test signals: enabling individual events while running gadget enumeration or transfers should show coherent command, TRB, request, and event sequences. Build failures here usually indicate trace macro misuse or type mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/ulpi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/ulpi.c

Purpose: registers a ULPI bus interface backed by DWC3 `GUSB2PHYACC` accesses so external USB2 PHY registers can be read and written through the controller.

Important APIs/functions: `dwc3_ulpi_init` and `dwc3_ulpi_exit` are exported to core code. Internal helpers are `dwc3_ulpi_busyloop`, `dwc3_ulpi_read`, `dwc3_ulpi_write`, and `dwc3_ulpi_detect_config`. `dwc3_ulpi_ops` supplies ULPI read/write callbacks.

Control flow: init registers a ULPI interface with DWC3-backed ops, stores it in `dwc->ulpi`, then detects specific PHY IDs. Reads and writes compose `GUSB2PHYACC` requests, support extended ULPI addresses, wait for `DONE` with nanosecond-scale delays, and return data or timeout. Exit unregisters the interface and clears the pointer.

State and persistence: persistent state is `dwc->ulpi` and feature flags such as `enable_usb2_transceiver_delay` set for Microchip USB3340. Register operations affect external PHY state through the DWC3 access window.

Dependencies and integration: uses Linux ULPI interface APIs, ULPI register constants, delays, time constants, and DWC3 IO/core helpers. It integrates with PHY management and DWC3 core initialization.

Risks: timeouts can occur if the PHY is absent, clocked incorrectly, or suspended. The busy loop briefly sleeps if SUSPHY is set, but callers still rely on hardware readiness. Extended address timing differs from normal reads/writes. Vendor-specific detection currently handles only Microchip USB3340.

Test signals: successful ULPI registration, readable PHY ID values, correct Microchip delay flag setting, and no timeout logs during probe/resume. Hardware tests should include PHY register reads, writes through ULPI drivers, and suspend/resume with SUSPHY transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/ulpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/early/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/early/Makefile

Purpose: wires early USB debug console objects into the kernel build based on Kconfig selections.

Important APIs/functions: no C API. Build targets are `ehci-dbgp.o` for `CONFIG_EARLY_PRINTK_DBGP` and `xhci-dbc.o` for `CONFIG_EARLY_PRINTK_USB_XDBC`.

Control flow: kbuild conditionally adds the corresponding object files to `obj-y`/`obj-m` style build lists according to config symbols.

State and persistence: none at runtime; it controls which early-console implementations are linked into the kernel.

Dependencies and integration: depends on Kconfig symbols defined elsewhere for early printk over EHCI debug port and xHCI debug capability. It sits under USB early drivers and feeds the top-level kernel build.

Risks: incorrect config symbols would silently exclude early console support. Building these objects in unsupported architectures/configurations can fail because the C files depend on early PCI, fixmap, and low-level x86-style direct PCI access.

Test signals: build with each config enabled, confirm the expected object is compiled, and boot with `earlyprintk=dbgp` or xDBC parameters to verify linked code is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/early/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/early/ehci-dbgp.c -->
# sources/distributed-fs/ceph-client/drivers/usb/early/ehci-dbgp.c

Purpose: implements a standalone EHCI debug-port early console and optional KGDB transport that can print over a USB debug device before normal USB host/device drivers are running.

Important APIs/functions: `early_dbgp_init` locates and initializes the EHCI debug port; `early_dbgp_console` provides the console write callback; `dbgp_reset_prep` and `dbgp_external_startup` integrate with later USB HCD reset/startup; KGDB support adds `kgdbdbgp_parse_config`, read/write callbacks, and a polling thread. Internal helpers scan PCI capabilities, map MMIO with fixmap, perform BIOS handoff, reset/start EHCI, wait/reset ports, issue debug-port control/bulk transfers, and handle vendor debug-port remapping.

Control flow: boot parameter parsing checks early PCI access, finds an EHCI controller with the debug capability, maps BAR0, computes capability/register/debug-port addresses, performs BIOS handoff, optionally remaps NVIDIA debug port selection, starts/reset EHCI, waits for a debug device, claims the debug port, enumerates the USB debug descriptor, assigns address 127, enables debug mode, and sends an initial sync write. Console writes split output into 8-byte packets, inject carriage returns before newlines, recover if EHCI stopped, and call debug bulk writes.

State and persistence: global static pointers track EHCI caps, operational regs, and debug regs. Other global state stores physical debug port, unsafe flag, IN/OUT endpoint numbers, and selected PCI device. KGDB state holds an 8-byte read buffer and polling controls. State persists from early boot into later USB handoff when `keep` or KGDB modes require it.

Dependencies and integration: uses early PCI direct access, fixmap, MMIO accessors, EHCI register definitions, USB control definitions, console infrastructure, optional KGDB, kthreads, and Xen debug hooks. It intentionally avoids relying on the normal USB stack for early output.

Risks: direct hardware ownership can conflict with BIOS or later EHCI HCD if handoff/reset sequencing is wrong. The code supports only simple 32-bit BAR0 debug ports. Unplug or timeouts set `dbgp_not_safe` to avoid hangs. Transfer loops are polling and can delay boot. The debug device must support the EHCI debug descriptor and tiny max packet size. Reset paths must release ownership unless the early console or KGDB still needs it.

Test signals: the source comment lists required boot cases: `earlyprintk=dbgp`, `earlyprintk=dbgp,keep`, `earlyprintk=dbgp console=ttyUSB0`, and combined VGA/dbgp modes, with EHCI HCD built in or absent. Additional signals are KGDB over dbgp, successful late HCD handoff, no boot hangs on unplug, and continued output across controller reset when `keep` is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/early/ehci-dbgp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/early/xhci-dbc.c -->
# sources/distributed-fs/ceph-client/drivers/usb/early/xhci-dbc.c

Purpose: implements early printk over the xHCI Debug Capability (DbC), including early PCI discovery, DbC context/ring setup, console writes, event processing, reset recovery, and cleanup or handoff after normal init.

Important APIs/functions: external init hooks are `early_xdbc_parse_parameter`, `early_xdbc_setup_hardware`, and `early_xdbc_register_console`. Internal code includes `xdbc_map_pci_mmio`, `xdbc_find_dbgp`, `xdbc_bios_handoff`, `xdbc_mem_init`, `xdbc_start`, `xdbc_bulk_transfer`, `xdbc_handle_external_reset`, `xdbc_handle_events`, `xdbc_bulk_write`, `early_xdbc_write`, `xdbc_scrub_function`, and `xdbc_init`.

Control flow: parameter parsing finds the selected xHCI PCI function, enables memory space, maps BAR MMIO with early ioremap, locates the debug extended capability, and stores DbC registers. Hardware setup hands off from BIOS, initializes a raw spinlock, allocates memblock pages for tables, buffers, event ring, IN ring, and OUT ring, writes descriptor strings and endpoint contexts, starts DbC, marks it initialized/configured, and posts an initial read. Console writes chunk output into 1024-byte packets with CRLF conversion, process events under a raw spinlock, wait for any previous OUT transfer, queue a TRB, set the cycle bit with a barrier, and ring the doorbell. Event handling consumes port status and transfer events, updates flags, reposts IN reads, and handles external reset by rebuilding contexts and restarting DbC. A subsys init hook either frees early resources or remaps MMIO for a kept console and runs a scrub thread until the connection ends.

State and persistence: `static struct xdbc_state xdbc` stores PCI identity, MMIO mapping, DbC registers, DMA/memblock tables, rings, buffers, port number, flags, and lock. Flags capture initialized, configured, stalls, and in-process transfers. `early_console_keep` controls whether the console remains after boot.

Dependencies and integration: depends on early PCI, memblock allocation, early and normal ioremap, xHCI register helpers, xHCI extended capability scanning, USB descriptor constants, console registration, raw spinlocks, kthreads, and xHCI DbC data structures from `xhci-dbc.h`.

Risks: early boot allocation failures can leak partially allocated memblock pages in some failure branches until cleanup. PCI bus mastering/memory enablement is forced. TRB cycle handling and event dequeue pointer updates are hardware-ordering sensitive. NMI writes use trylock and can drop output. External reset recovery must not race with console writes. Device-specific endpoint IDs differ between Intel and AMD-style implementations and are handled with alternate constants.

Test signals: boot with xDBC early console on supported xHCI hardware, verify early output before normal console, keep and non-keep cleanup modes, cable unplug/replug or external reset recovery, stalled endpoint handling, NMI printk behavior, and later host controller reuse. Trace output under `XDBC_TRACE` helps diagnose missed messages and event processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/early/xhci-dbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/early/xhci-dbc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/early/xhci-dbc.h

Purpose: defines the register layout, hardware data structures, constants, and software state used by the xHCI Debug Capability early console driver.

Important APIs/types/functions: key types are `struct xdbc_regs`, `xdbc_trb`, `xdbc_erst_entry`, `xdbc_info_context`, `xdbc_ep_context`, `xdbc_context`, `xdbc_strings`, `xdbc_segment`, `xdbc_ring`, and `xdbc_state`. It defines DbC control/status/port bits, descriptor identity values, string constants, ring sizes, endpoint ID variants, PCI scan limits, table layout constants, state flags, max packet size, doorbell target encoding, and `xdbc_read64`/`xdbc_write64` wrappers.

Control flow: the C file uses these layouts to map MMIO registers, allocate rings and descriptor tables, program ERST/DCCP/devinfo registers, queue TRBs, interpret event TRBs, track cycle state, and decide whether endpoint events refer to IN or OUT rings.

State and persistence: `struct xdbc_state` is the persistent early-console state container. It holds PCI coordinates, mapped xHCI base, DbC register pointer, DMA addresses, backing pages, rings, buffers, flags, port number, and a raw spinlock.

Dependencies and integration: includes Linux types and USB chapter 9 constants, and expects xHCI 64-bit accessor helpers to be available where included. It is private to early xDBC support.

Risks: structures mirror hardware ABI and require correct endianness and alignment. Endpoint ID differences across vendors are captured by duplicate constants; missing another variant would break event handling. Table size constants must remain consistent with allocations in `xhci-dbc.c`. The max packet and ring sizes drive transfer chunking and memory layout.

Test signals: compile-time layout use, successful DbC context programming, correct descriptor strings on the debug host, transfer events mapping to expected endpoints, and stable output across ring wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/early/xhci-dbc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/fotg210/Kconfig

Purpose: declares configuration options for the Faraday FOTG210 USB2 dual-role controller and its host/peripheral subdrivers.

Important APIs/functions: config symbols are `USB_FOTG210`, `USB_FOTG210_HCD`, and `USB_FOTG210_UDC`. The top-level option is tristate, depends on USB or USB_GADGET, DMA, IOMEM, and Gemini architecture or compile-test, defaults on Gemini, and selects `MFD_SYSCON`.

Control flow: when `USB_FOTG210` is enabled, users can select host controller support if USB linkage is compatible or peripheral support if USB gadget linkage is compatible. Help text explains module names and current peripheral bulk-transfer scope.

State and persistence: build-time configuration only. It determines which driver code is compiled and linked.

Dependencies and integration: integrates with Linux USB host and gadget Kconfig, architecture selection, compile testing, DMA/IOMEM availability, and Gemini syscon support needed by the core platform driver.

Risks: dependency expressions around built-in vs module linkage are important; invalid combinations could produce unresolved symbols or missing role support. The top-level dual-role controller does not imply dynamic role switching; actual mode is selected by device tree/dr_mode and core probing.

Test signals: `allmodconfig`/`allyesconfig`/`COMPILE_TEST`, Gemini defconfig, module builds for host and UDC, and boot tests in host and peripheral modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/fotg210/Makefile

Purpose: defines the object composition for the Faraday FOTG210 dual-role driver.

Important APIs/functions: no runtime API. `obj-$(CONFIG_USB_FOTG210) += fotg210.o`; `fotg210-y` always includes `fotg210-core.o`; optional objects are `fotg210-hcd.o` for host support and `fotg210-udc.o` for peripheral support.

Control flow: kbuild links one composite object whose contents depend on selected role subconfigs.

State and persistence: build-time state only. The selected objects determine which probe/remove calls in `fotg210-core.c` can resolve and execute.

Dependencies and integration: depends on the local Kconfig symbols and the top-level USB driver build system. It integrates core, HCD, and UDC sources into one driver/module.

Risks: if Kconfig permits a role symbol without the matching source object, core references to `fotg210_hcd_*` or `fotg210_udc_*` would fail at link time. If neither role is selected, the core object may build but have limited practical use.

Test signals: build matrix with host only, UDC only, both, built-in, and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-core.c

Purpose: provides central platform probing for the Faraday FOTG210 USB2 dual-role controller, including Gemini SoC-specific PHY/VBUS setup and dispatch to either the host controller or gadget controller subdriver.

Important APIs/functions: `fotg210_probe`, `fotg210_remove`, module init/exit, Gemini helper `fotg210_gemini_init`, and exported/shared `fotg210_vbus`. It calls subdriver hooks `fotg210_hcd_probe/remove/init/cleanup` and `fotg210_udc_probe/remove` depending on build and mode.

Control flow: probe allocates `struct fotg210`, maps MMIO, enables optional `PCLK`, reads `dr_mode`, performs Gemini syscon setup when compatible, reads the role register, warns if hardware role bits do not match requested mode, and calls UDC probe for peripheral mode or HCD probe otherwise. Remove chooses the same mode and calls the matching subdriver remove. Module init initializes HCD support if enabled and USB is not disabled, then registers the platform driver; exit unregisters and cleans up HCD support.

State and persistence: `struct fotg210` stores device, MMIO base/resource, clock, Gemini regmap, and port ID. Gemini syscon bits persistently select Mini-A/Mini-B role, VBUS, and wakeup bits in the global misc control register. `fotg210_vbus` mutates those VBUS bits at gadget-driver request.

Dependencies and integration: uses platform device resources, devm allocation and ioremap, optional clocks, OF matching, USB `dr_mode`, regmap/syscon for Gemini, string choice helpers, and host/gadget subdrivers in the same directory.

Risks: Gemini port detection relies on physical base address `0x69000000` for USB1 and treats others as USB0. There is no dynamic role switch; mode is fixed at probe. Hardware role mismatch is logged but does not abort. VBUS control silently returns for unknown port and depends on a valid syscon map. Module init ordering calls HCD global init before platform driver registration.

Test signals: probe on `faraday,fotg200`, `faraday,fotg210`, and `cortina,gemini-usb` compatible systems, host and peripheral `dr_mode`, VBUS toggling from gadget mode, wakeup-source property handling, clock enable failures, and remove/unload in both roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-core.c -->
