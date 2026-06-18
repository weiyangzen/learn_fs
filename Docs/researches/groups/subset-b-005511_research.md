# subset-b-005511 Research

Grouped source research for USB OHCI host-controller files under `sources/distributed-fs/ceph-client/drivers/usb/host`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-hcd.c

## Purpose

`ohci-hcd.c` is the main USB 1.1 Open Host Controller Interface core. It owns the generic `hc_driver` operations, controller setup/start/stop, interrupt handling, watchdog recovery, suspend/resume entry points, and module registration for several built-in bus glue drivers.

## Important APIs, Types, and Functions

Primary exported entry points are `ohci_setup()`, `ohci_init_driver()`, `ohci_restart()`, `ohci_suspend()`, and `ohci_resume()`. Core callbacks include `ohci_urb_enqueue()`, `ohci_urb_dequeue()`, `ohci_endpoint_disable()`, `ohci_get_frame()`, `ohci_start()`, `ohci_stop()`, and `ohci_irq()`. It includes `ohci-hub.c`, `ohci-dbg.c`, `ohci-mem.c`, and `ohci-q.c`, so those helpers are compiled as part of the core implementation.

## Control Flow

Bus glue creates a `usb_hcd`, maps registers, and calls the generic reset/start callbacks. `ohci_init()` handles BIOS/SMM ownership handoff, disables interrupts, discovers root-hub ports, allocates HCCA and descriptor pools, and creates debugfs files. `ohci_run()` resets the controller, programs HCCA, frame timing, control/bulk heads, root-hub power policy, enables root-hub polling, enters `OHCI_USB_OPER`, and enables interrupts. URB submission allocates `urb_priv` plus TDs, schedules the endpoint if idle, computes isochronous frame placement, then delegates TD construction to `td_submit_urb()`. IRQ handling reads enabled interrupt bits, handles unrecoverable errors, root-hub status changes, resume detect, done-head writeback, and unlink work until all pending enabled bits are drained.

## State and Persistence Behavior

Persistent runtime state is `struct ohci_hcd`, including register base, HCCA DMA buffer, control/bulk/periodic ED schedule, done-list pointers, pending URBs, EDs in use, root-hub state, frame timing, quirk flags, watchdog counters, and debugfs state. Hardware register state is reinitialized on start/restart/resume and forcibly reset on shutdown. No file-backed persistence exists.

## Dependencies and Integration Points

The file depends on USB core HCD APIs, DMA mapping, dma pools or local memory pools, debugfs, PCI quirk helpers, timers, workqueues, and OHCI register definitions from `ohci.h`. It integrates with bus glue through `ohci_init_driver()` overrides and with root hub logic through `ohci_hub_status_data()` and `ohci_hub_control()`.

## Risks and Test Signals

Risks include BIOS/SMM takeover timeouts, incorrect root-hub power/overcurrent firmware data, fragile hardware reset timing, lost done-head writebacks, frame counter stalls, late isochronous URBs, and quirk interactions across PCI/platform builds. Test signals include USB 1.1 enumeration, URB enqueue/dequeue across all pipe types, root-hub connect/disconnect interrupts, forced unlink paths, suspend/resume with remote wakeup, watchdog recovery on missing WDH, and module init/exit across enabled bus glue variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-hub.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-hub.c

## Purpose

`ohci-hub.c` implements OHCI root-hub behavior: hub status bitmaps, hub-control requests, port reset sequencing, root-hub suspend/resume, polling/autostop decisions, and OTG port reset support.

## Important APIs, Types, and Functions

Exported functions are `ohci_hub_status_data()` and `ohci_hub_control()`. PM builds add `ohci_rh_suspend()`, `ohci_rh_resume()`, `ohci_bus_suspend()`, and `ohci_bus_resume()`. Supporting helpers include `ohci_root_hub_state_changes()`, `ohci_hub_descriptor()`, `root_port_reset()`, `find_head()`, and optional `ohci_start_port_reset()`.

## Control Flow

Status polling reads hub and per-port change bits, clears RHSC before scanning ports, builds the USB hub change bitmap, and decides whether to keep polling or re-enable RHSC interrupts. Hub control maps USB hub requests to OHCI root-hub register writes, including clearing change bits, returning descriptors/status, powering ports, suspending ports, and issuing port reset pulses. Suspend first quiesces schedules, processes done/unlink work, optionally suspends every enabled port for global-suspend quirk hardware, configures remote wakeup, and writes `OHCI_USB_SUSPEND`. Resume handles normal resume, autostop resume, lost-power restart, schedule-head restoration, interrupt reenabling, and schedule restart.

## State and Persistence Behavior

The file mutates `ohci->hc_control`, `ohci->rh_state`, `ohci->autostop`, `ohci->next_statechange`, ED schedule heads, interrupt enables, and root-hub registers. Port power, reset, suspend, overcurrent, and change bits live in OHCI hardware registers. No persistent storage is used.

## Dependencies and Integration Points

It depends on USB hub class request constants, OHCI root-hub bit definitions, HCD polling flags, PM configuration, and `ohci_work()`/`update_done_list()` from queue handling. It is wired into the generic `hc_driver` root-hub callbacks and into `ohci_irq()` RHSC/RD paths.

## Risks and Test Signals

Risks include controller-specific RHSC level/edge behavior, races between polling and interrupt reenabling, reset timing on slow ports, suspend while schedules still hold retiring TDs, and autostop decisions that depend on remote-wakeup capability. Test signals include `GetHubDescriptor`, `GetPortStatus`, port power/reset/suspend requests, connect/disconnect wakeups, remote-wakeup resume, global-suspend quirk systems, and controllers with more than seven root ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-mem.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-mem.c

## Purpose

`ohci-mem.c` centralizes allocation and lookup for OHCI endpoint descriptors and transfer descriptors, plus basic initialization of controller-private lists and locks.

## Important APIs, Types, and Functions

Important helpers are `ohci_hcd_init()`, `ohci_mem_init()`, `ohci_mem_cleanup()`, `td_alloc()`, `td_free()`, `ed_alloc()`, `ed_free()`, and `dma_to_td()`. The file uses the `struct ed`, `struct td`, and TD hash table declared in `ohci.h`.

## Control Flow

Initialization sets `next_statechange`, initializes `ohci->lock`, and prepares pending and in-use ED lists. If the HCD does not provide a local memory pool, `ohci_mem_init()` creates DMA pools with OHCI-required TD and ED alignment. TD allocation returns a zeroed DMA-safe TD whose `hwNextTD` self-points until filled. ED allocation initializes the software TD list and stores the DMA address. TD free removes the TD from the DMA hash chain before returning memory to the pool.

## State and Persistence Behavior

State is entirely runtime memory: DMA pools, local memory allocations, TD hash chains, ED lists, and descriptor DMA addresses. Descriptors are coherent or local-memory-backed because hardware reads and writes them directly. No durable state exists.

## Dependencies and Integration Points

It depends on Linux DMA pool APIs, optional `usb_hcd.localmem_pool`, genalloc local memory helpers, and `ohci.h` descriptor layout. Queue handling uses `td_alloc()`/`ed_alloc()` during URB and endpoint setup, and done-list processing uses `dma_to_td()` to translate hardware done-head DMA values back to software TD objects.

## Risks and Test Signals

Risks include descriptor alignment mistakes, stale TD hash entries, freeing TDs still visible to hardware, local-memory pool address assumptions, and missing cleanup on partial initialization. Test signals include repeated endpoint enable/disable cycles, DMA API debugging, local-memory controllers such as SM501/SA1111, malformed done-head entries, and clean module unload after active URB churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-nxp.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-nxp.c

## Purpose

`ohci-nxp.c` is the platform OHCI driver for NXP LPC32xx-style USB host devices. It configures an ISP1301 USB transceiver over I2C, enables the SoC host bit and VBUS, and registers the generic OHCI core.

## Important APIs, Types, and Functions

Important functions are `isp1301_configure_lpc32xx()`, `isp1301_vbus_on()`, `isp1301_vbus_off()`, `ohci_nxp_start_hc()`, `ohci_nxp_stop_hc()`, `ohci_hcd_nxp_probe()`, and `ohci_hcd_nxp_remove()`. The global `isp1301_i2c_client` tracks the transceiver reference.

## Control Flow

Probe resolves the optional DT `transceiver` phandle, obtains the ISP1301 I2C client, coerces a 32-bit DMA mask, checks USB enablement, enables the host clock, programs ISP1301 mode registers for DAT_SE0 operation, creates the HCD, maps the OHCI MMIO resource, gets the IRQ, sets the SoC `HOST_EN` bit, drives VBUS, and calls `usb_add_hcd()`. Remove reverses HCD registration, disables host/VBUS, releases the HCD, and drops the transceiver device reference.

## State and Persistence Behavior

Driver state is minimal and mostly global: the ISP1301 client pointer plus clock/devm resources and HCD state. Hardware state persists in ISP1301 I2C registers and the LPC32xx USB OTG status/control register until reset or stop.

## Dependencies and Integration Points

It depends on platform bus, OF phandle lookup, I2C SMBus access, ISP1301 register definitions, clocks, DMA mask setup, and the generic OHCI `hc_driver` from `ohci_init_driver()`. It matches `nxp,ohci-nxp` and platform alias `usb-ohci`.

## Risks and Test Signals

Risks include the global transceiver pointer preventing multiple instances, unchecked I2C write failures, fixed `USB_CONFIG_BASE` ioremap, no suspend/resume support, and clock/transceiver ordering problems. Test signals include deferred probe until ISP1301 is present, correct VBUS drive, successful enumeration on LPC32xx, cleanup after `usb_add_hcd()` failure, and remove/reprobe without leaked I2C references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-nxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-omap.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-omap.c

## Purpose

`ohci-omap.c` is legacy OMAP1 OHCI platform glue. It handles OMAP clocks, optional OTG transceiver handoff, board-specific power and overcurrent setup, GPIO-backed port power, and platform PM around the generic OHCI core.

## Important APIs, Types, and Functions

`struct ohci_omap_priv` stores `usb_host_ck`, `usb_dc_ck`, and optional power/overcurrent GPIOs. Important functions are `omap_ohci_clock_power()`, `start_hnp()`, `ohci_omap_reset()`, `ohci_hcd_omap_probe()`, `ohci_hcd_omap_remove()`, `ohci_omap_suspend()`, and `ohci_omap_resume()`.

## Control Flow

Probe validates legacy resources, creates an HCD with extra private data, obtains optional GPIOs and the two clocks, maps registers, gets the IRQ, and calls `usb_add_hcd()`. The overridden reset path configures OTG if requested, enables clocks, invokes board reset hooks, calls `ohci_setup()`, sets remote-wakeup-connected state for OTG/RWC boards, applies OMAP OSK/Nokia770 root-hub policy, and powers transceivers or GPIOs. Suspend calls `ohci_suspend()` then disables clocks; resume re-enables clocks and calls `ohci_resume()`.

## State and Persistence Behavior

State lives in HCD private clock/GPIO pointers, `hcd->usb_phy`, OHCI root-hub registers, and board platform data callbacks. Power and mux state is hardware-backed and survives until explicit board or clock changes.

## Dependencies and Integration Points

It depends on OMAP1 SoC headers, legacy platform data `struct omap_usb_config`, OMAP mux and OTG registers, optional USB OTG PHY APIs, GPIO descriptors, clocks, and platform resources. It registers platform name `ohci`.

## Risks and Test Signals

Risks include legacy board conditionals, OTG handoff failure, missing unwind after some reset failures, global OMAP register assumptions, unused overcurrent GPIO, and power polarity differences. Test signals include OMAP OSK and Nokia770 boot, OTG HNP on configured port, clock enable/disable through PM, platform transceiver callbacks, GPIO power toggling, and root-hub descriptor power-budget behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-omap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-pci.c

## Purpose

`ohci-pci.c` is the PCI bus glue for generic USB OHCI controllers. It registers a PCI driver, applies controller-specific quirks before generic setup, and attaches PCI PM callbacks.

## Important APIs, Types, and Functions

Important functions include `ohci_pci_reset()`, `ohci_pci_probe()`, `ohci_pci_resume()`, and quirk callbacks `ohci_quirk_amd756()`, `ohci_quirk_ns()`, `ohci_quirk_zfmicro()`, `ohci_quirk_toshiba_scc()`, `ohci_quirk_nec()`, `ohci_quirk_amd700()`, `ohci_quirk_loongson()`, and `ohci_quirk_qemu()`. `ohci_pci_quirks[]` and `pci_ids[]` are the matching tables.

## Control Flow

Module init initializes the generic OHCI driver with a PCI reset override, installs PCI suspend/resume hooks, and registers `ohci_pci_driver`. Probe delegates most resource setup to `usb_hcd_pci_probe()`. Reset checks the quirk table for the PCI device, runs the quirk callback, calls `ohci_setup()`, and propagates PCI wakeup capability into `OHCI_CTRL_RWC`. NEC unrecoverable-error handling schedules a worker that calls `ohci_restart()`.

## State and Persistence Behavior

Persistent runtime state is in `ohci->flags`, optional NEC work item, modified `hcd->regs` for Loongson rev 0x02, and PCI core power-management state. Hardware quirk effects persist only for the lifetime of the HCD or current power state.

## Dependencies and Integration Points

It depends on PCI core matching/probing, `usb_hcd_pci_probe()`/remove/shutdown/PM helpers, `pci-quirks.h`, AMD PLL/prefetch helpers, and endian Kconfig options. It soft-depends on `ehci_pci` so EHCI companion handling loads first.

## Risks and Test Signals

Risks include quirk table regressions, unsupported big-endian Toshiba SCC builds, Loongson register-offset adjustment, AMD PLL/prefetch interaction with isochronous traffic, and broken suspend wakeup flags. Test signals include PCI OHCI enumeration, quirk-specific boot logs, suspend/resume across listed devices, NEC restart after injected UE, Loongson rev 0x02 register access, and companion EHCI coexistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-platform.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-platform.c

## Purpose

`ohci-platform.c` is the generic platform and devicetree OHCI driver. It handles clocks, optional shared resets, endian/port-count DT properties, runtime PM setup, and generic platform HCD registration.

## Important APIs, Types, and Functions

`struct ohci_platform_priv` stores up to four clocks and a reset-control array. Key functions are `ohci_platform_power_on()`, `ohci_platform_power_off()`, `ohci_platform_probe()`, `ohci_platform_remove()`, `ohci_platform_suspend()`, `ohci_platform_resume_common()`, `ohci_platform_resume()`, and `ohci_platform_restore()`.

## Control Flow

Probe supplies default platform data when none is provided, coerces a 32-bit DMA mask, gets IRQ, creates HCD with extra private state, parses DT endian and `num-ports` properties, obtains clocks and shared resets, validates endian Kconfig support, enables runtime PM, powers on clocks, maps registers, records TPL support, and calls `usb_add_hcd()`. Remove wakes the device, removes HCD, powers off, asserts resets, puts clocks, releases HCD, and disables runtime PM. Suspend calls generic OHCI suspend, powers off, and asserts resets; resume deasserts resets, powers on, calls `ohci_resume()`, and refreshes runtime PM state.

## State and Persistence Behavior

State consists of HCD private clock/reset handles, OHCI quirk flags from firmware properties, `ohci->num_ports`, runtime PM flags, and hardware reset/clock state. No durable data is stored.

## Dependencies and Integration Points

It depends on platform bus, OF properties from generic OHCI bindings, clock and reset frameworks, runtime PM, USB OF TPL helper, generic OHCI core, and optional board-supplied `usb_ohci_pdata`. It matches `generic-ohci`, `cavium,octeon-6335-ohci`, and `ti,ohci-omap3`.

## Risks and Test Signals

Risks include endian property/Kconfig mismatches, incomplete clock lists, shared reset ordering, runtime PM state imbalance, and platform-data versus DT default differences. Test signals include DT probes with big-endian properties, clock/reset failure injection, suspend/resume/restore, TPL property propagation, and remove/reprobe with all clocks released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-ppc-of.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-ppc-of.c

## Purpose

`ohci-ppc-of.c` is Open Firmware platform glue for PowerPC OHCI controllers. It supports little-endian and big-endian compatible strings, maps OF resources, and registers an OHCI HCD using core callbacks.

## Important APIs, Types, and Functions

Important functions are `ohci_ppc_of_start()`, `ohci_hcd_ppc_of_probe()`, and `ohci_hcd_ppc_of_remove()`. The file defines a dedicated `ohci_ppc_of_hc_driver`, OF match table, and `ohci_hcd_ppc_of_driver`.

## Control Flow

Probe rejects disabled USB, detects big-endian compatibles, translates the first OF address resource, creates an HCD, maps MMIO with `devm_ioremap_resource()`, maps the first OF IRQ, sets big-endian MMIO/descriptor flags and MPC5200 frame-number quirk when needed, initializes core state, and calls `usb_add_hcd()`. Start calls `ohci_init()` and `ohci_run()` directly. Remove unregisters the HCD, disposes the IRQ mapping, and releases the HCD. There is also an IBM 440EPx EHCI-related workaround path on failed add.

## State and Persistence Behavior

Runtime state is the HCD, mapped OF IRQ, resource mapping, and OHCI endian quirk flags. Hardware state is reset and initialized by the shared OHCI core. No persistent state exists.

## Dependencies and Integration Points

It depends on OF address/IRQ APIs, PowerPC endian Kconfig choices, platform bus registration from `ohci-hcd.c`, and generic OHCI core internals because it is included by the main module when configured.

## Risks and Test Signals

Risks include wrong compatible endianness, missing Kconfig endian selection, IRQ mapping leaks on errors, the unusual 440EPx fallback path, and direct use of core internals instead of `ohci_init_driver()`. Test signals include PPC OF probe for `ohci-be`, `ohci-bigendian`, and `ohci-le`, MPC5200 frame number behavior, IRQ disposal on remove, and enumeration on big-endian descriptor systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-ppc-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-ps3.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-ps3.c

## Purpose

`ohci-ps3.c` is PS3 system-bus glue for the OHCI controller behind the Cell/Spider platform. It opens hypervisor devices, creates PS3 DMA/MMIO/IRQ resources, applies PS3-specific big-endian and root-hub setup, and registers the generic OHCI core.

## Important APIs, Types, and Functions

Important functions are `ps3_ohci_hc_reset()`, `ps3_ohci_hc_start()`, `ps3_ohci_probe()`, `ps3_ohci_remove()`, `ps3_ohci_driver_register()`, and `ps3_ohci_driver_unregister()`. It defines `ps3_ohci_hc_driver` and `ps3_ohci_driver`.

## Control Flow

Probe checks firmware support, opens the HV device, creates DMA and MMIO regions, sets up an I/O IRQ, sets a 32-bit DMA mask, creates the HCD, requests and maps MMIO, stores HCD drvdata, and calls `usb_add_hcd()`. Reset marks MMIO big-endian and runs `ohci_init()`. Start preprograms root-hub descriptor A/B for Spider quirks, then calls `ohci_run()`. Remove shuts down OHCI, removes the HCD, unmaps/releases regions, destroys IRQ, frees DMA/MMIO regions, and closes the HV device.

## State and Persistence Behavior

State is held by PS3 system-bus device regions, virtual IRQ, HCD, and OHCI quirk flags. Hardware state is mediated by PS3 hypervisor resources and OHCI registers. No persistent data is written.

## Dependencies and Integration Points

It depends on PS3 firmware feature detection, `ps3_system_bus`, LV1 region helpers, PS3 IRQ setup, DMA region APIs, and the OHCI core included by `ohci-hcd.c`.

## Risks and Test Signals

Risks include hypervisor resource failure unwinding, `BUG_ON()` on unexpected DMA-region failure, nonfatal `request_mem_region()` failure followed by later release, big-endian MMIO assumptions, and shutdown using remove semantics. Test signals include PS3 firmware-gated registration, successful region/IRQ creation, root-hub power timing, USB enumeration on PS3, and full remove/shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-ps3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-pxa27x.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-pxa27x.c

## Purpose

`ohci-pxa27x.c` is PXA27x/PXA3x OHCI platform glue. It programs PXA-specific USB host registers, supports DT-to-platform-data conversion, controls optional per-port VBUS regulators, and overrides hub control for port power.

## Important APIs, Types, and Functions

`struct pxa27x_ohci` stores the USB clock, MMIO base, three VBUS regulators, and per-port regulator state. Important functions are `pxa27x_ohci_select_pmm()`, `pxa27x_ohci_set_vbus_power()`, `pxa27x_ohci_hub_control()`, `pxa27x_setup_hc()`, `pxa27x_reset_hc()`, `pxa27x_start_hc()`, `pxa27x_stop_hc()`, `ohci_pxa_of_init()`, probe/remove, and PM callbacks.

## Control Flow

Probe converts DT properties into `pxaohci_platform_data` if present, gets IRQ and clock, creates HCD with private state, maps registers, obtains enabled-port VBUS regulators, starts hardware, selects port power-management mode, forces `ohci->num_ports = 3`, then registers the HCD. The overridden hub-control callback intercepts port power set/clear to enable or disable matching VBUS regulators before delegating to generic `ohci_hub_control()`. Suspend calls `ohci_suspend()` and stops PXA hardware; resume restarts hardware, reapplies PMM mode, and calls `ohci_resume()`.

## State and Persistence Behavior

State includes platform data flags, clock state, PXA UHC register programming, VBUS regulator enable flags, HCD state, and hard-coded three-port root-hub state. Hardware register settings persist while clocks and reset state remain active.

## Dependencies and Integration Points

It depends on PXA SoC helpers, `platform_data/usb-ohci-pxa27x.h`, regulator framework, clocks, OF properties named `marvell,*`, USB OTG pin-hold clearing, and generic OHCI callbacks initialized through `ohci_init_driver()`.

## Risks and Test Signals

Risks include busy-waiting indefinitely for `UHCHR_FSBIR`, unchecked regulator-get errors stored in the array, VBUS index assumptions, DT/platform-data parity, hard-coded three ports, and platform callback failures. Test signals include all PMM modes, per-port regulator toggling from hub requests, DT property parsing, suspend/resume with VBUS state, and enumeration on enabled ports only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-pxa27x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-q.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-q.c

## Purpose

`ohci-q.c` is the OHCI transfer scheduler and completion engine. It creates endpoint descriptors, schedules control/bulk/interrupt/iso EDs, builds TD chains for URBs, processes hardware done lists, handles endpoint halts, unlinks EDs/URBs safely, and gives URBs back to USB drivers.

## Important APIs, Types, and Functions

Important helpers include `urb_free_priv()`, `finish_urb()`, `balance()`, `periodic_link()`, `ed_schedule()`, `periodic_unlink()`, `ed_deschedule()`, `ed_get()`, `start_ed_unlink()`, `td_fill()`, `td_submit_urb()`, `td_done()`, `ed_halted()`, `add_to_done_list()`, `update_done_list()`, `finish_unlinks()`, `takeback_td()`, `process_done_list()`, and `ohci_work()`.

## Control Flow

URB enqueue obtains or creates an ED, schedules it if idle, and calls `td_submit_urb()`. TD submission builds transfer descriptors by pipe type: control setup/data/status, bulk/interrupt 4 KiB chunks with optional zero packet, and one TD per isochronous packet. Periodic EDs are balanced into the 32-branch schedule tree by frame load, while control and bulk EDs form tail-linked lists. Hardware completion writes a done-head chain; `update_done_list()` converts DMA TDs through the hash table and normalizes halted EDs; `process_done_list()` computes lengths/status and completes URBs. Unlink requests deschedule EDs, wait at least until the next frame, patch TD chains, finish unlinked URBs, then either idle or reschedule the ED.

## State and Persistence Behavior

The file mutates ED state (`IDLE`, `OPER`, `UNLINK`), TD lists, pending URB list, done-list pointers, periodic load accounting, endpoint toggle carry, HCD bandwidth counters, AMD quirk state for isochronous traffic, and control/bulk/periodic hardware schedule registers. No durable persistence exists.

## Dependencies and Integration Points

It depends on `ohci-mem.c` allocation/hash helpers, `ohci.h` descriptor formats, USB core URB/endpoint APIs, DMA addresses prepared by HCD glue, `usb_calc_bus_time()`, AMD PCI quirk helpers, and `ohci_irq()`/watchdog calls into `update_done_list()` and `ohci_work()`.

## Risks and Test Signals

Risks include schedule-tree load bugs, races while hardware sees EDs being unlinked, short-read and halt recovery corner cases, isochronous late-frame handling, data-toggle preservation during unlink, done-list hash corruption, and reentrant completion callbacks. Test signals include bulk SG transfers, control requests with/without data, interrupt bandwidth limits, isochronous ASAP and late URBs, URB cancellation storms, endpoint disable waiting paths, and injected TD error condition codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-s3c2410.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-s3c2410.c

## Purpose

`ohci-s3c2410.c` is Samsung S3C2410 OHCI platform glue. It manages host and bus clocks, platform-data port power, platform overcurrent reporting, and overrides root-hub status/control to expose board-specific power and overcurrent state.

## Important APIs, Types, and Functions

Important functions are `s3c2410_start_hc()`, `s3c2410_stop_hc()`, `ohci_s3c2410_hub_status_data()`, `s3c2410_usb_set_power()`, `ohci_s3c2410_hub_control()`, `s3c2410_hcd_oc()`, `ohci_hcd_s3c2410_probe()`, remove, and PM callbacks. It uses platform data `struct s3c2410_hcd_info`.

## Control Flow

Probe powers both possible ports through platform callbacks, creates and maps the HCD, gets `usb-host` and `usb-bus-host` clocks, gets IRQ, starts clocks, installs overcurrent callbacks in platform data, then calls `usb_add_hcd()`. Module init overrides generic hub status/control callbacks. Hub status ORs platform overcurrent change bits into the root-hub bitmap. Hub control intercepts power and overcurrent feature requests and edits hub descriptors and port status to reflect board capabilities. Overcurrent callback records status/change and powers down affected ports.

## State and Persistence Behavior

State is split between global clock pointers, HCD state, and platform data fields `hcd`, `report_oc`, per-port `power`, `oc_status`, and `oc_changed`. Hardware clock and power state persists until stop or platform callbacks reverse it.

## Dependencies and Integration Points

It depends on Samsung platform data, platform callbacks for power and overcurrent enablement, clocks, platform resources, and generic OHCI core callbacks. It registers platform name `s3c2410-ohci`.

## Risks and Test Signals

Risks include global clock pointers limiting multiple instances, platform-data-only design, direct cast of hub status buffer to `u32 *`, overcurrent state not protected by a normal lock, and port numbering limited to 1 and 2. Test signals include port power callbacks from hub requests, overcurrent interrupt simulation, hub descriptor changes for per-port power/OCPM, suspend/resume clock cycling, and enumeration after overcurrent clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-s3c2410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-sa1111.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-sa1111.c

## Purpose

`ohci-sa1111.c` is SA-1111 companion-chip bus glue for OHCI. It powers and resets the SA-1111 USB block, sets up local memory to work around SA-1111 DMA addressing errata, and binds the core OHCI callbacks to the SA-1111 bus.

## Important APIs, Types, and Functions

Important functions are `ohci_sa1111_reset()`, `ohci_sa1111_start()`, `sa1111_start_hc()`, `sa1111_stop_hc()`, `ohci_hcd_sa1111_probe()`, `ohci_hcd_sa1111_remove()`, and `ohci_hcd_sa1111_shutdown()`. The file defines SA-1111 USB reset/status bit masks and `ohci_sa1111_hc_driver`.

## Control Flow

Probe creates the HCD, gets the SA-1111 USB IRQ, configures a 64 KiB local-memory bounce pool to avoid DMA erratum constraints, reserves the register region, uses the already-mapped SA-1111 base as HCD registers, starts hardware, and adds the HCD. Starting hardware programs power sense/control polarity for Assabet, asserts interface/HC reset, enables the SA-1111 device clock, delays, and releases reset. Remove unregisters the HCD, stops hardware, releases the region, and drops the HCD. Shutdown calls the HCD shutdown callback and stops hardware if still accessible.

## State and Persistence Behavior

State is HCD local memory pool, SA-1111 device clock/reset state, memory region reservation, and OHCI core runtime state. Reset and clock state live in SA-1111 registers and are not persisted beyond hardware state.

## Dependencies and Integration Points

It depends on SA-1111 bus APIs, SA-1111 register mapping, machine detection for Assabet, USB local-memory support, and generic OHCI internals because it is included by `ohci-hcd.c` when configured.

## Risks and Test Signals

Risks include local-memory sizing assumptions, SA-1111 DMA erratum constraints, edge-triggered IRQ behavior, polarity assumptions for Assabet, and no explicit PM callbacks beyond shutdown. Test signals include probe on SA-1111 systems, bounce-buffer use under DMA debug, enumeration with memory above the erratum boundary, shutdown path with hardware accessible, and remove/reprobe without region leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-sa1111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-sm501.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-sm501.c

## Purpose

`ohci-sm501.c` is OHCI glue for the SM501 multifunction device. It uses SM501 local memory for DMA, powers and unmasks the USB host block, and integrates the generic OHCI core with SM501 platform resources.

## Important APIs, Types, and Functions

Important functions are `ohci_sm501_init()`, `ohci_sm501_start()`, `ohci_hcd_sm501_drv_probe()`, `ohci_hcd_sm501_drv_remove()`, `ohci_sm501_suspend()`, and `ohci_sm501_resume()`. It defines `ohci_sm501_hc_driver` and `ohci_hcd_sm501_driver`.

## Control Flow

Probe gets IRQ, reserves the SM501 local-memory resource and OHCI register resource, creates the HCD, maps registers, initializes core state, sets up `usb_hcd_setup_local_mem()` so USB buffers are copied into SM501-local DMA memory when needed, adds the HCD, enables wakeup, powers the SM501 USB host gate, and unmasks the SM501 interrupt. Remove unregisters the HCD, unmaps/releases resources, masks the interrupt, and powers the USB host off. PM suspend calls `ohci_suspend()` and powers off; resume powers on and calls `ohci_resume()`.

## State and Persistence Behavior

State is in platform resources, local-memory pool, HCD/OHCI structures, SM501 power gate, and SM501 IRQ mask. Local memory contents and register state are runtime-only and reset by remove/suspend.

## Dependencies and Integration Points

It depends on SM501 MFD APIs, SM501 register definitions, platform resources with separate register and local-memory windows, local-memory HCD support, and OHCI core internals included by the main module.

## Risks and Test Signals

Risks include resource index assumptions, enabling power after `usb_add_hcd()` rather than before, shared IRQ masking order, local-memory offset calculations, and PM without reinitializing all SM501-specific state. Test signals include SM501 probe with two MEM resources, local-memory DMA transfers, interrupt delivery after unmask, suspend/resume enumeration, and cleanup after `usb_add_hcd()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-sm501.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-spear.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-spear.c

## Purpose

`ohci-spear.c` is ST SPEAr platform OHCI glue. It is a compact driver that supplies a clock-backed platform wrapper around the generic OHCI core.

## Important APIs, Types, and Functions

`struct spear_ohci` stores the interface clock. Important functions are `spear_ohci_hcd_drv_probe()`, `spear_ohci_hcd_drv_remove()`, `spear_ohci_hcd_drv_suspend()`, and `spear_ohci_hcd_drv_resume()`. It defines `ohci_spear_hc_driver`, `spear_ohci_id_table`, and platform driver `spear_ohci_hcd_driver`.

## Control Flow

Probe gets IRQ, coerces a 32-bit DMA mask, obtains the clock, creates an HCD with extra private clock storage, maps MMIO, enables the clock, and calls `usb_add_hcd()`. Remove removes the HCD, disables the clock, and releases the HCD. Suspend waits for state-change quiet time, calls `ohci_suspend()`, and disables the clock. Resume re-enables the clock and calls `ohci_resume()`.

## State and Persistence Behavior

Runtime state is the HCD, mapped registers, and a single clock pointer in private data. Clock state is the only platform-specific hardware state managed here. There is no persistence.

## Dependencies and Integration Points

It depends on platform bus, OF match `st,spear600-ohci`, clock framework, DMA mask setup, platform MMIO/IRQ resources, and generic OHCI `ohci_init_driver()` callbacks.

## Risks and Test Signals

Risks include ignored `clk_prepare_enable()` return in probe/resume, no reset or PHY handling, no `usb_disabled()` check until module init, and simple PM ordering. Test signals include SPEAr DT probe, clock enable/disable observation, enumeration, suspend/resume with device wakeup policy, and failure cleanup before/after HCD allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-spear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-st.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-st.c

## Purpose

`ohci-st.c` is STMicroelectronics OHCI platform glue for `st,st-ohci-300x`. It extends generic platform handling with multiple clocks, optional 48 MHz clock rate programming, power and soft reset controls, and a USB PHY.

## Important APIs, Types, and Functions

`struct st_ohci_platform_priv` stores up to three clocks, optional `clk48`, power and softreset reset controls, and a PHY. Important functions are `st_ohci_platform_power_on()`, `st_ohci_platform_power_off()`, `st_ohci_platform_probe()`, `st_ohci_platform_remove()`, `st_ohci_suspend()`, and `st_ohci_resume()`.

## Control Flow

Probe gets IRQ, creates an HCD with private state, gets the USB PHY, collects unnamed OF clocks, obtains optional 48 MHz clock and reset controls, powers on by deasserting power/reset, setting `clk48` to 48 MHz, enabling clocks, initializing and powering the PHY, maps registers, and calls `usb_add_hcd()`. Remove unregisters the HCD, powers off, releases clocks, and drops the HCD. Suspend calls `ohci_suspend()` then platform power-off; resume powers on and calls `ohci_resume()`.

## State and Persistence Behavior

State includes clock handles, reset handles, PHY state, HCD/OHCI state, and platform data pointing at default power callbacks. Hardware state is reset/clock/PHY controlled and not persisted after power-off.

## Dependencies and Integration Points

It depends on OF platform resources, clock framework, reset framework, generic PHY API, `usb_ohci_pdata`, generic OHCI initialization, and `st,st-ohci-300x` binding data.

## Risks and Test Signals

Risks include asserting power before softreset on power-off, optional reset semantics, PHY init/power unwind ordering, missing runtime PM compared with generic platform driver, and assuming unnamed clock order. Test signals include PHY/reset/clock failure injection, 48 MHz rate programming, suspend/resume, probe deferral for PHY/clocks/resets, and clean remove after active devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci.h

## Purpose

`ohci.h` is the shared OHCI core contract. It defines hardware descriptor layouts, register layouts, bit masks, private HCD state, endian conversion helpers, root-hub register access helpers, quirk flags, and exported symbols used by bus glue drivers.

## Important APIs, Types, and Functions

Key types are `struct ed`, `struct td`, `struct ohci_hcca`, `struct ohci_regs`, `struct urb_priv`, `enum ohci_rh_state`, `struct ohci_hcd`, and `struct ohci_driver_overrides`. Important helpers include `hcd_to_ohci()`, `ohci_to_hcd()`, `_ohci_readl()`, `_ohci_writel()`, `cpu_to_hc16/32()`, `hc16/32_to_cpu()`, `ohci_frame_no()`, `ohci_hwPSW()`, `periodic_reinit()`, and root-hub readers. Exported declarations include `ohci_init_driver()`, `ohci_restart()`, `ohci_setup()`, `ohci_suspend()`, `ohci_resume()`, `ohci_hub_control()`, and `ohci_hub_status_data()`.

## Control Flow

The header has no standalone runtime path, but its inline accessors are executed throughout the OHCI core. Descriptor endian helpers mediate every CPU/hardware ED and TD field. Register helpers select little-endian or big-endian MMIO based on Kconfig and quirk flags. `periodic_reinit()` reprograms frame interval and periodic start after reset/resume.

## State and Persistence Behavior

The header defines all important runtime state but stores none by itself. `struct ohci_hcd` persists for the HCD lifetime and contains hardware mappings, DMA memory, schedules, quirk flags, PM state, watchdog state, debugfs, and platform private extension storage.

## Dependencies and Integration Points

It depends on Linux USB HCD, endian helpers, MMIO accessors, DMA types, list heads, timers, work structs, and debugfs types supplied by including C files. It is included by core and bus glue files, making it the ABI-like internal interface for all OHCI variants.

## Risks and Test Signals

Risks include endian-helper regressions, incorrect descriptor alignment or masks, root-hub bit definition errors, quirk flag collisions, frame-number handling on big-endian hosts, and structure layout changes affecting every bus glue driver. Test signals include build coverage across little-endian, big-endian, and mixed-endian configs; sparse/endian warnings; USB enumeration on multiple buses; isochronous PSW handling; and root-hub port status correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci.h -->
