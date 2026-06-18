# subset-b-005508 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mv.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mv.c

## Purpose
Marvell/PXA EHCI platform glue. It allocates an EHCI HCD, maps the Marvell register layout with capability registers at `0x100`, handles optional OTG host registration, enables clocks/PHYs, drives VBUS for host mode, and applies HSIC-specific port setup before delegating transfers to the shared EHCI core.

## Important APIs, types, and functions
`struct ehci_hcd_mv` stores mode, mapped base/cap/op register pointers, OTG/PHY/clock handles, and a platform `set_vbus` callback. `mv_ehci_enable()` and `mv_ehci_disable()` sequence clock and PHY lifetime. `mv_ehci_reset()` sets `hcd->has_tt`, calls `ehci_setup()`, and toggles `PORT_TEST_FORCE` for HSIC. `mv_ehci_probe()`, `mv_ehci_remove()`, and `mv_ehci_shutdown()` provide platform-driver lifecycle. `platform_overrides` supplies the reset hook and private size to `ehci_init_driver()`.

## Control flow
Probe checks `usb_disabled()`, creates the HCD, pulls platform data, gets an optional generic PHY plus a required clock, maps MMIO, enables hardware, computes caps/op register pointers, gets IRQ, and sets `ehci->caps`. OTG mode registers the host with the transceiver and disables local power until OTG activates it. Host mode asserts VBUS, calls `usb_add_hcd()`, and enables wakeup. Remove unregisters the HCD if present, detaches OTG host state, clears VBUS, disables PHY/clock for host mode, and releases the HCD.

## State and persistence behavior
Software state lives in `ehci_hcd_mv` under `ehci->priv` and in USB core HCD state. Hardware state persists in Marvell EHCI/PHY registers, port status bits, VBUS, clock gating, and OTG host binding until remove, reset, or power loss.

## Dependencies and integration points
Depends on platform device resources, clocks, generic PHY, legacy USB PHY/OTG, `mv_usb_platform_data`, device-tree PHY mode, and shared EHCI symbols from `ehci.h`. It matches `marvell,pxau2o-ehci` and legacy platform IDs `pxa-u2oehci`/`pxa-sph`.

## Risks and edge cases
The register offset assumptions are Marvell-specific. OTG mode intentionally disables local clock/PHY after `otg_set_host()`, so host-mode and OTG-mode teardown differ. HSIC setup writes reserved-looking port bits and depends on accurate DT PHY mode. Error paths must undo VBUS, clock, PHY, and HCD ownership in the right order.

## Test signals
Probe/remove in host and OTG modes, deferred PHY probing, clock failure, IRQ absence, HSIC DT mode, VBUS callback behavior, root-hub registration, suspend wakeup capability, and module unload are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-npcm7xx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-npcm7xx.c

## Purpose
Nuvoton NPCM7xx EHCI platform glue. It provides a minimal OpenFirmware platform driver that sets a 32-bit DMA mask, maps EHCI registers starting at offset zero, registers the HCD, and wires suspend/resume to the common EHCI power-management helpers.

## Important APIs, types, and functions
The main entry points are `npcm7xx_ehci_hcd_drv_probe()`, `npcm7xx_ehci_hcd_drv_remove()`, `ehci_npcm7xx_drv_suspend()`, and `ehci_npcm7xx_drv_resume()`. `ehci_npcm7xx_hc_driver` is initialized by `ehci_init_driver()` without custom overrides. The OF match table accepts `nuvoton,npcm750-ehci`.

## Control flow
Probe rejects disabled USB, obtains IRQ 0, coerces a 32-bit coherent DMA mask, creates an HCD, maps the first memory resource, records resource bounds, points `hcd_to_ehci(hcd)->caps` at `hcd->regs`, then calls `usb_add_hcd()` with `IRQF_SHARED`. Remove calls `usb_remove_hcd()` and `usb_put_hcd()`. Suspend delegates to `ehci_suspend()` with wakeup policy; resume calls `ehci_resume(hcd, false)`.

## State and persistence behavior
There is no driver-private state. Runtime state is the HCD/EHCI core state plus mapped hardware registers. The DMA mask setting persists on the device object for allocations made by USB core/EHCI pools.

## Dependencies and integration points
Depends on platform resources, OF matching, DMA mapping, USB HCD core, and common EHCI implementation. It uses `usb_hcd_platform_shutdown` for platform shutdown.

## Risks and edge cases
The driver assumes capability registers begin at resource offset zero. It has no explicit clocks, resets, or PHY handling, so board firmware/SoC integration must leave the controller powered and clocked. Missing `platform_set_drvdata()` is covered by `usb_add_hcd()`/HCD platform behavior only if the core stores it as expected for remove.

## Test signals
NPCM750 DT probe, DMA mask setup, IRQ sharing, root-hub enumeration, system suspend/resume with and without wakeup, shutdown, and repeated module bind/unbind are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-npcm7xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-omap.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-omap.c

## Purpose
TI OMAP3/OMAP4 EHCI host glue. It binds the EHCI core to OMAP USBHOST platform data, manages per-port USB PHYs, enables runtime PM, writes an OMAP EHCI unsuspend workaround register, and registers the host controller.

## Important APIs, types, and functions
`struct omap_hcd` tracks up to `OMAP3_HS_USB_PORTS` PHY pointers and port count. `ehci_hcd_omap_probe()` and `ehci_hcd_omap_remove()` own lifecycle. `ehci_write()` writes raw OMAP EHCI insn registers. `EHCI_INSNREG04_DISABLE_UNSUSPEND` disables an undocumented behavior where clearing Run/Stop unsuspends ports. `ehci_omap_overrides` only adds private storage.

## Control flow
Probe requires a parent device and platform data, pulling parent platform data for DT children. It maps MMIO, coerces a 32-bit DMA mask, creates the HCD, sets resource metadata and caps, then gets PHYs by `phys` phandle for each configured port. PHY-mode ports are initialized and unsuspended before `usb_add_hcd()`. Runtime PM is enabled and synchronously acquired, the OMAP workaround bit is written, and then non-PHY modes such as HSIC bring their reset-modeled PHY out of suspend after the HCD is live. Remove unregisters the HCD, shuts down all PHYs, drops the HCD, and disables runtime PM.

## State and persistence behavior
Driver-private state is limited to `struct omap_hcd`. Persistent external state includes PHY init/suspend state, runtime-PM active usage count, and the EHCI insn register workaround bit. Port configuration comes from platform data and remains board-specific.

## Dependencies and integration points
Depends on OMAP USB platform data (`usbhs_omap_platform_data`), legacy USB PHY APIs, runtime PM, DT phandles, DMA mapping, and shared EHCI core. It matches `ti,ehci-omap`.

## Risks and edge cases
The DT path depends on parent platform data. PHY failures after some ports were initialized require full cleanup. Runtime PM `pm_runtime_get_sync()` return value is not checked, so PM errors could be hidden. The undocumented register write is essential for suspend stability and should not be removed casually.

## Test signals
OMAP3/4 host probe, multiple port modes, missing or deferred PHYs, HSIC reset PHY behavior, runtime suspend/resume, root-hub suspend with the unsuspend workaround, remove after partial probe failure, and DMA allocation coverage are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-omap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-orion.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-orion.c

## Purpose
Marvell Orion/Armada/AC5 EHCI glue. It configures DMA masks, optional clocks, MBUS DRAM windows, Orion PHY errata registers, Armada 3700 SBUSCFG, and then registers a shared EHCI HCD with caps at `regs + 0x100`.

## Important APIs, types, and functions
`struct orion_ehci_hcd` stores the optional clock. `orion_usb_phy_v1_setup()` implements Orion USB controller guidelines and errata programming. `ehci_orion_conf_mbus_windows()` mirrors DRAM chip-select windows into USB address-decode registers. `ehci_orion_drv_reset()` calls `ehci_setup()` and applies the Armada 3700 SBUSCFG workaround. `ehci_orion_drv_probe()`, remove, suspend, and resume provide lifecycle. OF match data selects 32-bit or AC5 34-bit DMA masks.

## Control flow
Probe gets IRQ, coerces DMA mask from compatible data, maps MMIO, creates the HCD, sets caps/resource state and integrated TT, enables an optional clock, configures MBUS windows if present, applies legacy PHY setup for non-DT platform data, and calls `usb_add_hcd()`. Remove unregisters the HCD, disables the optional clock, and releases the HCD. PM routes to `ehci_suspend()`/`ehci_resume()`.

## State and persistence behavior
State lives in `struct orion_ehci_hcd`, HCD/EHCI core fields, and MMIO registers. MBUS windows, PHY tuning, SBUSCFG, interrupt masks, and host-mode bits persist until controller reset or driver teardown.

## Dependencies and integration points
Depends on Marvell MBUS helpers, platform data for legacy PHY version, OF match data, clock APIs, DMA mapping, and common EHCI code. Compatible strings include `marvell,orion-ehci`, `marvell,armada-3700-ehci`, and `marvell,ac5-ehci`.

## Risks and edge cases
`of_device_get_match_data()` must provide a valid DMA mask pointer for DT devices. Legacy non-DT `pd` is dereferenced when no OF node is present. PHY setup contains busy-wait reset loops with no timeout. MBUS windows are limited to four entries, matching the register block.

## Test signals
DT probe for all compatibles, AC5 memory above 4 GiB, optional clock absence/presence, MBUS window programming, Armada 3700 SBUSCFG after reset, suspend/resume, remove, and USB enumeration under DMA stress are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-orion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-pci.c

## Purpose
PCI bus glue for EHCI controllers. It matches generic PCI EHCI class devices, applies vendor/device-specific quirks before and after `ehci_setup()`, handles PCI MWI and suspend/resume reinitialization, and delegates normal PCI HCD management to USB core helpers.

## Important APIs, types, and functions
`ehci_pci_setup()` is the reset/setup hook. `ehci_pci_reinit()` enables PCI MWI and programs Intel Quark thresholds. `ehci_pci_resume()` resumes via common EHCI and reinitializes if needed. `ehci_pci_probe()` bypasses known devices with dedicated drivers. `pci_overrides` installs the reset hook; module init fills `pci_suspend` and `pci_resume` in the generated `hc_driver`.

## Control flow
Probe rejects bypass IDs and calls `usb_hcd_pci_probe()`. During setup, the driver sets `ehci->caps = hcd->regs`, applies pre-setup quirks such as endian MMIO, NVIDIA coherent mask reduction, integrated TT flags, AMD PLL/dummy-QH workarounds, VIA sleep timing, Synopsys/Aspeed flags, and Zhaoxin wakeup handling. It detects an EHCI debug port, calls `ehci_setup()`, then applies post-setup quirks, fixes bogus companion-port counts for some controllers, reads SBRN when available, enables legacy wakeup when needed, and runs PCI reinit. Remove clears MWI and delegates teardown.

## State and persistence behavior
State is mostly quirk bits in `struct ehci_hcd`, PCI config values, DMA mask constraints, `ehci->debug`, SBRN, and MWI state. Workarounds alter hardware thresholds, PCI config bytes, and EHCI schedule behavior for the device lifetime.

## Dependencies and integration points
Depends on PCI core, USB PCI HCD helpers, `pci-quirks.h`, AMD USB quirk helpers, EHCI core, and USB PM ops. It integrates with all generic PCI EHCI controllers via `PCI_CLASS_SERIAL_USB_EHCI`, plus an STMicro host ID.

## Risks and edge cases
Quirk ordering matters because DMA allocation constraints must precede `ehci_setup()`, while some controller bits must follow reset. The generic class match can bind hardware that really needs a specialized driver unless bypassed. Vendor-specific assumptions affect memory safety, wakeup, schedule unlinking, and debug-port access.

## Test signals
Probe/remove on Intel, NVIDIA, AMD/ATI, VIA, Aspeed, Huawei/Synopsys, NetMos, Zhaoxin, and generic controllers; hibernation restore; debug-port detection; large-memory DMA; dummy-QH scheduling; IAA watchdog behavior; and PCI PM wakeup are critical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-platform.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-platform.c

## Purpose
Generic platform/OF/ACPI EHCI glue. It supplies default clock/reset/power handling, supports platform data overrides, parses common DT endian and quirk properties, handles suspend/resume, and includes an R-Car Gen3 polling workaround that rebinds the companion controller when port status sticks.

## Important APIs, types, and functions
`struct ehci_platform_priv` stores up to four clocks, reset array, reset-on-resume flag, and polling timer/work. `ehci_platform_reset()` sets Synopsys/no-watchdog/Broadcom FIFO quirks and calls `ehci_setup()`. `ehci_platform_power_on()`/`power_off()` manage clocks. `ehci_platform_probe()`, remove, suspend, and resume own lifecycle. `quirk_poll_check_port_status()`, `quirk_poll_timer()`, and `quirk_poll_work()` implement the R-Car recovery path.

## Control flow
Probe selects platform data or defaults, coerces a 32-bit or 64-bit DMA mask, creates the HCD, parses DT properties for endian descriptors/registers, spurious over-current, reset-on-resume, integrated TT, Aspeed, and R-Car polling, acquires clocks and resets, validates endian config options, powers on, maps MMIO, sets TPL support, and calls `usb_add_hcd()`. Remove stops poll work, removes the HCD, powers off, asserts resets, drops clocks, and clears default platform data. Suspend stops polling, suspends EHCI, powers down, and asserts reset; resume reverses reset/power, waits for a companion device if present, resumes EHCI, refreshes runtime PM state, and restarts polling.

## State and persistence behavior
State spans `ehci_platform_priv`, platform data callbacks, HCD/EHCI quirk flags, clocks, resets, timer/work items, and hardware registers. Runtime PM active state is reestablished on resume.

## Dependencies and integration points
Depends on OF/ACPI/platform matching, clock/reset frameworks, `usb_ehci_pdata`, USB companion lookup, sys_soc matching, DMA mapping, and EHCI core. It matches generic, VIA/WonderMedia, Cavium Octeon, Aspeed AST2700, and ACPI `PNP0D20`.

## Risks and edge cases
Default platform data is temporarily installed on the device and must be cleared. Clock acquisition handles `-EPROBE_DEFER` specially. Endian DT properties require matching Kconfig support. The R-Car workaround intentionally unbinds/rebinds a companion driver from delayed work, which is powerful and timing-sensitive.

## Test signals
DT and ACPI probe, clock counts from zero to four, reset failures, endian property combinations, 64-bit DMA match data, Aspeed and Broadcom quirks, R-Car stuck-port recovery, suspend/resume with companion wait, TPL support, and failure-path cleanup are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-ppc-of.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-ppc-of.c

## Purpose
PowerPC OpenFirmware EHCI glue, especially for AMCC PPC 440EPx. It defines a complete `hc_driver`, maps OF resources/IRQs, supports big-endian MMIO/descriptors, enables a 440EPx Break Memory Transfer erratum bit, and coordinates with a companion OHCI controller for the AMCC USB23 erratum.

## Important APIs, types, and functions
`ehci_ppc_of_hc_driver` directly lists EHCI callbacks. `ppc44x_enable_bmt()` maps the second resource and writes `PPC440EPX_EHCI0_INSREG_BMT`. `ehci_hcd_ppc_of_probe()` and remove manage resources. `set_ohci_hcfs()` from `ehci.h` is used on removal when `has_amcc_usb23` is set.

## Control flow
Probe resolves OF memory resource and IRQ mapping, creates an HCD, maps registers, finds an IBM OHCI companion node, maps its control register if present, parses endian properties, sets caps, applies the 440EPx BMT workaround when compatible, calls `usb_add_hcd()`, and enables wakeup. Remove unregisters the HCD, disposes IRQ mapping, conditionally restores OHCI operational state if the companion appears loaded, and releases the HCD.

## State and persistence behavior
EHCI state lives in the HCD plus `ehci->has_amcc_usb23`, endian flags, and `ohci_hcctrl_reg`. Hardware state includes BMT and companion OHCI HCFS bits.

## Dependencies and integration points
Depends on OF address/IRQ APIs, PPC endian IO helpers, shared EHCI core, and optional IBM OHCI companion nodes. It matches compatible `usb-ehci`.

## Risks and edge cases
The direct `hc_driver` must remain synchronized with shared EHCI callback expectations. IRQ mappings are manually disposed. Companion OHCI coordination relies on probing resource ownership with `request_mem_region()`, which is indirect. Big-endian properties require Kconfig support in the shared helpers.

## Test signals
PPC OF probe/remove, 440EPx BMT register programming, big-endian descriptor/register operation, OHCI companion present/absent, IRQ mapping failure, and suspend/resume through bus callbacks are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-ppc-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-ps3.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-ps3.c

## Purpose
Sony PS3 system-bus EHCI driver. It opens PS3 hypervisor devices, creates DMA/MMIO regions, maps interrupts, configures PS3-specific EHCI internal setup registers after reset, and exposes a complete EHCI `hc_driver`.

## Important APIs, types, and functions
`ps3_ehci_setup_insnreg()` applies PS3 errata fix 316 for reset-lost internal registers. `ps3_ehci_hc_reset()` enables big-endian MMIO, sets caps, calls `ehci_setup()`, then restores the insn registers. `ps3_ehci_probe()` and `ps3_ehci_remove()` manage hypervisor, DMA, MMIO, IRQ, HCD, and memory resources. `ps3_ehci_driver_register()` only registers on PS3 LV1 firmware.

## Control flow
Probe rejects disabled USB, opens the hypervisor device, creates DMA and MMIO regions, maps an I/O IRQ, installs a dummy 32-bit DMA mask, creates the HCD, requests and ioremaps MMIO, stores drvdata, and calls `usb_add_hcd()`. Remove unregisters the HCD, clears drvdata, unmaps/releases MMIO, destroys IRQ and PS3 regions, frees DMA, and closes the HV device. Shutdown is the same as remove.

## State and persistence behavior
State spans PS3 system-bus region descriptors, virtual IRQ, HCD fields, and PS3 EHCI insn registers. The insn register settings must be rewritten after every EHCI reset because hardware resets them.

## Dependencies and integration points
Depends on PS3 firmware feature detection, PS3 system bus, hypervisor region APIs, big-endian MMIO helpers, DMA APIs, and shared EHCI callbacks.

## Risks and edge cases
The probe failure ladder is long and must release resources in reverse order. `BUG_ON()` is used for unexpected PS3 region and remove states. Shutdown equals remove, so double-remove style paths must not occur. Big-endian descriptors are not set, only MMIO.

## Test signals
Boot on PS3 LV1 firmware, no-op registration on non-PS3 firmware, probe failure at each HV/DMA/MMIO/IRQ/HCD step, reset reprogramming of insn registers, root-hub enumeration, remove/shutdown, and IRQ delivery are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-ps3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-q.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-q.c

## Purpose
Core EHCI queue-head and queue-element-transfer-descriptor engine for control, bulk, and interrupt transfers. It builds qTD chains from URBs, appends them to endpoint QHs using the EHCI dummy-qTD pattern, links/unlinks QHs on async or periodic schedules, processes completions, handles errors and TT buffer cleanup, and works around several controller unlink/writeback quirks.

## Important APIs, types, and functions
Important helpers include `qtd_fill()`, `qh_update()`, `qh_refresh()`, `qtd_copy_status()`, `qh_completions()`, `qh_urb_transaction()`, `qh_make()`, `qh_append_tds()`, `submit_async()`, `intr_submit()` through the scheduler side, `qh_link_async()`, `start_unlink_async()`, `start_iaa_cycle()`, `end_iaa_cycle()`, `end_unlink_async()`, `unlink_empty_async()`, and `scan_async()`. `ehci_clear_tt_buffer_complete()` is exported through `hc_driver`.

## Control flow
URB submission first converts a control/bulk/interrupt URB into one or more qTDs, including setup/status stages, scatterlist fragments, zero-packet termination, data toggles, IOC, and short-read alternate-next behavior. The QH is created per endpoint if needed, initialized for high/full/low speed and TT metadata, and appended by swapping the first new qTD into the previous dummy qTD so hardware never sees a half-built queue. Async QHs are linked after the async head and schedule activation is requested. Completion scanning walks qTDs up to active hardware state, translates tokens into URB status and actual lengths, gives back completed URBs, clears TT buffers for non-stall split errors, and requests QH unlinking when halted, short-read, empty, or dummy-overlay recovery is needed. Async unlinking removes QHs from the hardware list, requests IAA, runs a watchdog for lost IAA, often waits through two cycles, and relinks queued QHs if more work arrived.

## State and persistence behavior
Persistent runtime state includes endpoint `hcpriv` QHs, qTD lists, QH state (`LINKED`, `UNLINK`, `IDLE`, etc.), unlink lists, async activity counts, data toggles in usbcore, TT clearing state, retry counters, and DMA descriptors in EHCI pools. Hardware state is the async schedule and QH overlays modified by the controller.

## Dependencies and integration points
Depends on EHCI descriptor definitions in `ehci.h`, USB core URB/endpoint APIs, DMA pools, TT clear-buffer requests, hrtimer events from `ehci-timer.c`, interrupt scheduling hooks from `ehci-sched.c`, and root-hub state from the common EHCI core.

## Risks and edge cases
The dummy-qTD swap and memory barriers are critical for avoiding hardware races. Short reads, halted QHs, active unlinks, and controller writeback after IAA are all subtle. Full/low-speed TT buffer cleanup intentionally skips STALLs because some hubs misbehave. Async unlink logic contains controller-specific two-cycle and active-stability delays; simplifying it can corrupt memory on affected hardware.

## Test signals
Control transfers with setup/data/status, bulk scatter-gather, `URB_ZERO_PACKET`, short reads with and without `URB_SHORT_NOT_OK`, stalls, babble, DBE, MMF, XactErr retries, unlink/dequeue during giveback, TT clear-buffer completion, lost IAA watchdog, dummy-QH quirk devices, and high concurrency on async queues are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sched.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sched.c

## Purpose
EHCI periodic scheduler for interrupt and isochronous transfers. It manages the periodic frame list and shadow list, allocates high-speed iTD and full/low-speed split siTD descriptors, reserves high-speed and TT bandwidth, schedules URBs into microframes, scans completions, and coordinates delayed unlink/free operations.

## Important APIs, types, and functions
Periodic list helpers are `periodic_next_shadow()`, `shadow_next_periodic()`, and `periodic_unlink()`. TT and bandwidth helpers include `find_tt()`, `drop_tt()`, `compute_tt_budget()`, `reserve_release_intr_bandwidth()`, `reserve_release_iso_bandwidth()`, `check_period()`, `check_intr_schedule()`, and `qh_schedule()`. Interrupt paths use `intr_submit()`, `scan_intr()`, `qh_link_periodic()`, `start_unlink_intr_wait()`, and `end_unlink_intr()`. Iso paths use `iso_stream_find()`, `iso_stream_schedule()`, `itd_submit()`, `sitd_submit()`, `itd_link_urb()`, `sitd_link_urb()`, `itd_complete()`, `sitd_complete()`, and `scan_isoc()`.

## Control flow
Interrupt URBs share QH/qTD construction with `ehci-q.c` but run through periodic placement. The scheduler finds or reuses a phase, checks per-microframe bandwidth and TT collision/budget constraints, writes S-mask/C-mask bits, reserves bandwidth, and links the QH into all required frame-list slots sorted after iso entries. Empty interrupt QHs are unlinked after a delay so common one-URB interrupt endpoints can be reused cheaply. Iso submission builds an endpoint `ehci_iso_stream`, precomputes packet descriptors, allocates iTDs or siTDs, schedules start time with underrun and `URB_ISO_ASAP` handling, links descriptors into periodic frames, and enables the periodic schedule. Completion scanning walks from `last_iso_frame` to current frame, leaves active descriptors in current frames, removes completed descriptors, updates packet status/length/error counts, gives back URBs, and caches descriptors for delayed safe freeing.

## State and persistence behavior
State includes periodic hardware frame list, `pshadow`, interrupt QH list, iso stream lists/free lists, TT objects stored in `usb_tt->hcpriv`, global `bandwidth[]`, per-TT bandwidth, computed `tt_budget[]`, `last_iso_frame`, `now_frame`, and USB core bandwidth counters. The hardware consumes periodic descriptors asynchronously, so descriptors are cached before pool-free to avoid immediate reuse hazards.

## Dependencies and integration points
Depends on `ehci.h` QH/iTD/siTD/FSTN structures, queue helpers from `ehci-q.c`, hrtimer events from `ehci-timer.c`, USB bandwidth calculation helpers, TT topology from usbcore, and AMD PLL quirk helpers for active isochronous traffic.

## Risks and edge cases
Periodic scheduling is sensitive to off-by-one frame/microframe math, wraparound, TT carryover, and bandwidth release symmetry. Full-speed split IN scheduling avoids late uframes and does not implement all FSTN possibilities. Reusing descriptors too soon can trigger silicon corruption. URBs too far in the future return `-EFBIG`; URBs entirely in the past may complete immediately with errors counted.

## Test signals
High-speed interrupt and high-bandwidth interrupt endpoints, FS/LS interrupt behind single-TT and multi-TT hubs, bandwidth exhaustion, sysfs `uframe_periodic_max` changes, high-speed iso IN/OUT, split iso IN/OUT, `URB_ISO_ASAP`, underrun/overflow paths, queue teardown while active, descriptor free delay, and AMD PLL transitions are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sh.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sh.c

## Purpose
SuperH EHCI platform driver. It defines a direct `hc_driver`, maps platform resources, optionally enables SuperH USB interface/function clocks, and registers the shared EHCI core.

## Important APIs, types, and functions
`struct ehci_sh_priv` stores optional `iclk`/`fclk` and the HCD pointer. `ehci_sh_reset()` sets caps to `hcd->regs` and calls `ehci_setup()`. `ehci_hcd_sh_probe()`, `ehci_hcd_sh_remove()`, and `ehci_hcd_sh_shutdown()` provide lifecycle. `ehci_sh_hc_driver` lists common EHCI callbacks directly.

## Control flow
Probe obtains IRQ, creates the HCD, maps MMIO, allocates private state, gets optional `usb_fck` and `usb_ick`, enables both clocks, calls `usb_add_hcd()`, enables wakeup, stores drvdata, and returns. Remove removes the HCD, releases it, and disables clocks. Shutdown calls the HCD shutdown callback if installed.

## State and persistence behavior
State is in `ehci_sh_priv`, HCD/EHCI structures, clock-enable state, and MMIO registers. There is no suspend/resume device PM wrapper in this file, though the `hc_driver` includes bus suspend/resume when built with PM.

## Dependencies and integration points
Depends on platform resources, clock framework, USB HCD core, and common EHCI callbacks available because this file is included in or built with the EHCI core context. It registers under platform name `sh_ehci`.

## Risks and edge cases
It calls `clk_enable()` on optional clocks that may be `NULL`; this relies on common clock API tolerance. `devm_kzalloc()` state stores the HCD, but the HCD itself is manually owned. No DMA mask is set here, so platform setup must provide one if required.

## Test signals
Probe with both clocks, one clock, and no clocks; IRQ/mapping failures; root-hub enumeration; shutdown; remove; and clock enable/disable balance are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-spear.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-spear.c

## Purpose
ST SPEAr SoC EHCI platform glue. It sets a 32-bit DMA mask, manages a required USB host clock, maps registers starting at zero, registers the HCD, and wires simple suspend/resume to the common EHCI helpers.

## Important APIs, types, and functions
`struct spear_ehci` stores the clock in EHCI private storage. `spear_ehci_hcd_drv_probe()` and remove own lifecycle. `ehci_spear_drv_suspend()` and `ehci_spear_drv_resume()` call common EHCI PM. `spear_overrides` adds private space to the generated `hc_driver`.

## Control flow
Probe checks USB disabled state, gets IRQ, coerces 32-bit DMA, gets the clock, creates the HCD, maps MMIO, records resources, stores the clock in private state, sets caps to `hcd->regs`, enables the clock, and calls `usb_add_hcd()`. Remove removes the HCD, disables the clock, and releases the HCD.

## State and persistence behavior
The only private state is the clock pointer. Runtime state is held by HCD/EHCI core and the enabled clock. Register state persists in the controller until reset or power gating.

## Dependencies and integration points
Depends on OF platform matching (`st,spear600-ehci`), clock framework, DMA mapping, PM ops, and shared EHCI core. Uses `usb_hcd_platform_shutdown`.

## Risks and edge cases
Clock acquisition is mandatory. Like other minimal glue, it assumes caps at offset zero and no reset/PHY sequencing. Failure paths must balance clock enable and HCD ownership.

## Test signals
SPEAr DT probe, DMA mask setup, clock failure/defer, suspend/resume, remove, shared IRQ operation, and root-hub enumeration are the main tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-spear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-st.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-st.c

## Purpose
STMicroelectronics EHCI platform glue for `st,st-ehci-300x`. It manages multiple clocks, optional 48 MHz rate programming, power and soft resets, a generic PHY, pinctrl sleep/default states, a packet-buffer threshold register, and shared EHCI registration.

## Important APIs, types, and functions
`struct st_ehci_platform_priv` stores three general clocks, `clk48`, power/reset controls, and PHY. `st_ehci_platform_reset()` writes a 128-byte IN/OUT threshold to `AHB2STBUS_INSREG01`, sets caps with `pdata->caps_offset`, and calls `ehci_setup()`. `st_ehci_platform_power_on()` and `power_off()` sequence resets, clocks, and PHY. Probe/remove plus `st_ehci_suspend()`/`st_ehci_resume()` own lifecycle.

## Control flow
Probe creates the HCD, installs default platform data, gets required PHY, enumerates OF clocks, optionally gets `clk48`, gets optional shared power and soft-reset controls, powers on, maps MMIO, and calls `usb_add_hcd()`. Power-on deasserts power then soft reset, sets `clk48` to 48 MHz if present, enables clocks, initializes and powers on PHY. Suspend calls `ehci_suspend()`, powers down, and selects pinctrl sleep. Resume selects default pinctrl, powers on, and calls `ehci_resume()`.

## State and persistence behavior
State lives in private clock/reset/PHY handles and default platform data. Hardware state includes reset lines, clock enables, PHY power, pinctrl state, and threshold register configuration.

## Dependencies and integration points
Depends on clock, reset, PHY, pinctrl PM, OF, DMA/HCD core, `usb_ehci_pdata`, and EHCI shared code. It matches `st,st-ehci-300x`.

## Risks and edge cases
Probe error handling after successful `power_on()` jumps to clock cleanup without explicitly calling `power_off()`, so failures after power-on should be reviewed for resource state. `power_off()` asserts resets before powering off/exiting PHY, which must match hardware requirements. Optional reset controls may be NULL and must be accepted by reset APIs.

## Test signals
Probe with all clocks and without `clk48`, reset-defer paths, PHY power failures, threshold register programming, suspend/resume pinctrl transitions, remove after active traffic, and failure after power-on are high-value signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sysfs.c

## Purpose
Sysfs support included by the EHCI core. It exposes companion-controller port ownership and the maximum periodic microframe bandwidth setting for runtime inspection/tuning.

## Important APIs, types, and functions
`companion_show()` lists ports dedicated to a companion controller. `companion_store()` parses `portnum` or `-portnum`, updates `ehci->companion_ports`, and calls `set_owner()`. `uframe_periodic_max_show()` displays `ehci->uframe_periodic_max`. `uframe_periodic_max_store()` validates and updates the limit under `ehci->lock`. `create_sysfs_files()` and `remove_sysfs_files()` install/remove attributes.

## Control flow
On EHCI initialization, sysfs creation adds `companion` unless the controller has an integrated TT, then adds `uframe_periodic_max`. Writes to `companion` validate the port range and immediately program ownership. Writes to `uframe_periodic_max` parse an integer, require 100 through 124 usec/uframe, and refuse decreases below already allocated periodic bandwidth.

## State and persistence behavior
State is `ehci->companion_ports`, hardware PORT_OWNER bits, `ehci->uframe_periodic_max`, and current `bandwidth[]` accounting. Values persist only for the HCD lifetime and can affect subsequent periodic scheduling.

## Dependencies and integration points
Depends on device sysfs, EHCI root-hub helpers, `set_owner()`, `ehci_is_TDI()`, and scheduler bandwidth accounting.

## Risks and edge cases
Changing port ownership at runtime can disconnect or hand devices to companion controllers. Lowering bandwidth is protected by a lock and allocation scan, but raising to non-standard limits is allowed with a warning. The `companion` file is absent for integrated-TT controllers.

## Test signals
Sysfs file presence/absence, valid and invalid companion port writes, owner bit changes, `uframe_periodic_max` invalid values, refusal below allocated bandwidth, successful increase/decrease, and concurrent periodic URB submission are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-timer.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-timer.c

## Purpose
Shared EHCI hrtimer event engine. It serializes deferred controller work: async/periodic schedule state polling, controller-death cleanup, interrupt and async QH unlink completion, delayed iTD/siTD freeing, IAA watchdog recovery, schedule disable delays, and I/O watchdog scans.

## Important APIs, types, and functions
`ehci_set_command_bit()` and `ehci_clear_command_bit()` update cached USBCMD and flush posted writes. `event_delays_ns[]` and `event_handlers[]` must match `enum ehci_hrtimer_event`. `ehci_enable_event()` schedules pending events. Handlers include `ehci_poll_ASS()`, `ehci_poll_PSS()`, `ehci_handle_controller_death()`, `ehci_handle_start_intr_unlinks()`, `ehci_handle_intr_unlinks()`, `start_free_itds()`, `end_free_itds()`, `ehci_iaa_watchdog()`, `turn_on_io_watchdog()`, and `ehci_hrtimer_func()`.

## Control flow
Callers enable an event with optional timeout refresh. The timer tracks the lowest-numbered pending event rather than a sorted queue. On expiration, `ehci_hrtimer_func()` takes `ehci->lock`, snapshots enabled events, clears the set, handles expired events, and re-enables unexpired ones. Poll handlers wait for hardware status bits to match command bits before enabling/disabling schedules. Unlink handlers age QHs through wait lists. The IAA watchdog fabricates progress when hardware loses or delays IAA. Controller death disables configured flag/interrupts and runs cleanup work.

## State and persistence behavior
Timer state is `enabled_hrtimer_events`, `next_hrtimer_event`, `hr_timeouts[]`, poll counters, unlink cycles/lists, `iaa_in_progress`, cached command bits, and delayed descriptor free sentinels. Hardware state includes USBCMD, USBSTS, configured flag, and interrupt enable registers.

## Dependencies and integration points
Depends on EHCI core lock discipline, queue/scheduler unlink functions from `ehci-q.c` and `ehci-sched.c`, hrtimer APIs, and the common `ehci_work()` scan path.

## Risks and edge cases
The enum, delay array, and handler array must stay in identical order. Timer callbacks run under spinlock, so handlers cannot sleep. Event priority is approximate and may delay work up to roughly twice its nominal delay. Lost IAA and controller-death paths are recovery-critical.

## Test signals
Async and periodic schedule enable/disable races, delayed empty-QH unlink, interrupt QH unlink wait, active async unlink, lost IAA injection, controller halt/death, isoch descriptor free delay, I/O watchdog scans, and suspend/remove with pending events are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-xilinx-of.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-xilinx-of.c

## Purpose
Xilinx OpenFirmware EHCI host glue. It supports Xilinx XPS USB host cores with big-endian registers/descriptors, caps at offset `0x100`, optional full-speed support, and custom warning messages when unsupported non-high-speed devices cannot be enabled.

## Important APIs, types, and functions
`ehci_xilinx_port_handed_over()` reports likely LS/FS incompatibility when a port cannot be enabled. `ehci_xilinx_of_hc_driver` directly lists common EHCI callbacks and uses the custom `port_handed_over` hook. `ehci_hcd_xilinx_of_probe()` and remove manage OF resources and HCD lifecycle.

## Control flow
Probe resolves memory resource and IRQ from the device tree, creates the HCD, maps MMIO, marks both MMIO and descriptors big-endian, reads `xlnx,support-usb-fs` to set `hcd->has_tt`, points caps to `regs + 0x100`, and registers the HCD. Remove removes and releases the HCD.

## State and persistence behavior
State is in HCD/EHCI endian flags, `has_tt`, resource metadata, and mapped registers. Device-tree hardware configuration controls whether full-speed support is advertised for the HCD lifetime.

## Dependencies and integration points
Depends on OF address/IRQ/platform APIs, big-endian EHCI Kconfig support, USB HCD core, and shared EHCI callbacks. It matches `xlnx,xps-usb-host-1.00.a`.

## Risks and edge cases
The core always forces big-endian descriptor and register access; missing Kconfig support would break operation. IRQ mappings are not explicitly disposed on every failure/remove path. The warning hook can conflate power failures with unsupported speed, as noted in comments.

## Test signals
Probe on HS-only and FS-capable Xilinx cores, big-endian descriptor operation, LS/FS device insertion, high-speed enumeration, IRQ mapping failure, remove, and port enable failures are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-xilinx-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci.h

## Purpose
Central private header for the Linux EHCI host-controller implementation. It defines the EHCI controller state object, DMA descriptor layouts, queue/schedule metadata, endian accessors, timer events, quirk flags, TT bandwidth structures, and exported interfaces used by bus glue and shared EHCI source files.

## Important APIs, types, and functions
Core types include `struct ehci_hcd`, `struct ehci_qtd`, `struct ehci_qh_hw`, `struct ehci_qh`, `struct ehci_iso_stream`, `struct ehci_itd`, `struct ehci_sitd`, `struct ehci_fstn`, `struct ehci_tt`, and `struct ehci_driver_overrides`. Important enums/macros cover root-hub state, hrtimer events, qTD/QH token bits, periodic type tags, descriptor endian conversions, root-hub TT helpers, Freescale/ChipIdea errata predicates, and logging wrappers. Export declarations include `ehci_init_driver()`, `ehci_setup()`, `ehci_reset()`, `ehci_suspend()`, `ehci_resume()`, `ehci_hub_control()`, and related helpers.

## Control flow
The header itself has no runtime control path, but its structures drive all EHCI paths. Bus glue allocates `struct ehci_hcd` inside `usb_hcd`, sets caps/register pointers and quirks, and calls shared setup. Queue code manipulates qTD/QH fields defined here. Scheduler code manipulates iTD/siTD/FSTN/TT structures. Timer code uses the event enum and `struct ehci_hcd` fields to coordinate deferred work.

## State and persistence behavior
`struct ehci_hcd` is the persistent per-controller state for schedule lists, DMA pools, root-hub port bitmaps, timer state, quirk flags, bandwidth accounting, and private bus-glue storage. Hardware-visible descriptor structs are DMA-backed and must match EHCI-specified alignment and endian rules.

## Dependencies and integration points
Includes EHCI register definitions from `linux/usb/ehci_def.h` and integrates with USB HCD core, DMA pool users, platform/PCI glue, root-hub code, queue/scheduler/timer/sysfs/debug files, and architecture-specific endian IO helpers.

## Risks and edge cases
Descriptor layout, alignment, bit definitions, and endian conversions are ABI-critical for hardware DMA. `struct ehci_hcd` private storage must remain last. Timer enum order must match arrays in `ehci-timer.c`. Quirk flags are shared across many bus drivers and core paths, so adding or repurposing flags can change broad behavior.

## Test signals
Builds across little-endian and big-endian MMIO/descriptor configs, sparse endian checks, all bus glue drivers, async and periodic transfer tests, suspend/resume, root-hub TT behavior, quirk-specific hardware, and structure-size/alignment checks are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-dbg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-dbg.c

## Purpose
DebugFS support for the Freescale QUICC Engine FHCI host controller. It tracks USB interrupt causes and exposes FHCI controller registers and interrupt statistics under the USB debugfs root.

## Important APIs, types, and functions
`fhci_dbg_isr()` increments per-interrupt counters, using slot 12 for idle-only when `usb_er == -1`. `fhci_dfs_regs_show()` emits key `qe_usb_ctlr` registers and line state. `fhci_dfs_irq_stat_show()` emits named interrupt counters. `fhci_dfs_create()` creates the per-device debugfs directory and `regs`/`irq_stat` files. `fhci_dfs_destroy()` recursively removes them.

## Control flow
The FHCI interrupt path calls `fhci_dbg_isr()` with the event register value. Debugfs reads call the seq-file show functions, which read MMIO registers with `in_8()`/`in_be16()` and return formatted snapshots. Driver initialization/teardown calls create/destroy for the debugfs nodes.

## State and persistence behavior
State is `fhci->usb_irq_stat[]`, `fhci->dfs_root`, and live hardware register contents. Counters persist for the HCD lifetime and are reset only by allocation/reinitialization.

## Dependencies and integration points
Depends on `fhci.h`, Linux debugfs/seq_file, USB debug root, QUICC Engine USB register layout, and `fhci_ioports_check_bus_state()`. It is diagnostic and does not alter controller state.

## Risks and edge cases
Debugfs creation errors are not checked, which is typical but means diagnostics may silently be absent. Counter updates are not synchronized, so debug reads may race interrupt updates and provide approximate values. Register reads assume the controller remains mapped and alive while debugfs files exist.

## Test signals
Debugfs node creation/removal, register read output, interrupt counter increments for each bit and idle-only, repeated bind/unbind, debugfs reads during interrupt activity, and reads after teardown ordering are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/fhci-dbg.c -->
