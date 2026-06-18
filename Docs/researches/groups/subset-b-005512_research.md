# Research: subset-b-005512

Grouped research for USB host controller sources under `sources/distributed-fs/ceph-client/drivers/usb/host`. Each section is bounded for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/oxu210hp-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/oxu210hp-hcd.c

## Purpose
This file implements the platform HCD for Oxford Semiconductor OXU210HP, a quasi-EHCI USB 2.0 host controller exposing two logical host controllers, OTG and SPH, behind shared top-level chip registers. It embeds EHCI register definitions, queue-head and qTD structures, an on-chip memory allocator, async and periodic schedules, root-hub emulation, interrupt handling, and platform-driver probe/remove glue.

## Important APIs, Types, and Functions
Key local hardware types are `struct ehci_caps`, `struct ehci_regs`, `struct ehci_qtd`, `struct ehci_qh`, `union ehci_shadow`, `struct oxu_onchip_mem`, `struct oxu_murb`, and `struct oxu_hcd`. `struct oxu_hcd` is the controller-private state: MMIO register pointers, on-chip memory bitmap pools, async QH, reclaim queue, periodic schedule, root-hub port state, timers, and split-URB resource tracking.

The exported integration surface is the `oxu_hc_driver` method table: `.reset = oxu_reset`, `.start = oxu_run`, `.stop = oxu_stop`, `.shutdown = oxu_shutdown`, `.urb_enqueue = oxu_urb_enqueue`, `.urb_dequeue = oxu_urb_dequeue`, `.endpoint_disable = oxu_endpoint_disable`, `.get_frame_number = oxu_get_frame`, `.hub_status_data = oxu_hub_status_data`, `.hub_control = oxu_hub_control`, and PM bus callbacks. The platform entry points are `oxu_drv_probe`, `oxu_drv_remove`, and `oxu_drv_shutdown`, registered by `module_platform_driver(oxu_driver)`.

Memory management is centered on `ehci_mem_init`, `ehci_mem_cleanup`, `ehci_qtd_alloc`, `oxu_qtd_free`, `oxu_qh_alloc`, `oxu_qh_free`, `oxu_buf_alloc`, `oxu_buf_free`, `oxu_murb_alloc`, and `oxu_murb_free`. Queue construction and scheduling are handled by `qh_urb_transaction`, `qh_make`, `qh_append_tds`, `submit_async`, `intr_submit`, `qh_link_async`, `start_unlink_async`, `end_unlink_async`, `scan_async`, `qh_schedule`, `qh_link_periodic`, `qh_unlink_periodic`, and `scan_periodic`.

## Control Flow
Probe maps the platform MMIO resource, sets the IRQ trigger, allocates `struct oxu_info`, runs `oxu_configuration`, verifies the chip ID in `oxu_verify_id`, then calls `oxu_create` twice to create OTG and SPH HCDs sharing the same base mapping and IRQ. Each HCD reset (`oxu_reset`) selects either OTG or SPH capability/operational register windows and the opposite on-chip memory region, initializes locks and resource queues, then calls `oxu_hcd_init`.

Startup (`oxu_run`) resets the EHCI core, installs the periodic frame list and async head DMA addresses, configures segment addressing, sets RUN and CONFIGFLAG, and enables EHCI interrupt bits. Shutdown/stop halt or reset the core, turn off ports, clean schedules, delete timers, and free software allocations while leaving the chip in a state suitable for reboot or handoff.

URB submission first builds qTD chains with `qh_urb_transaction`, including OXU-local data buffers for every transfer. Control, bulk, and interrupt transfers share QH/qTD machinery. Bulk URBs larger than 4096 bytes are split by `oxu_urb_enqueue` into `struct oxu_murb` micro URBs whose `complete == NULL` marks them as internal fragments; completion of the last fragment gives back the original URB. Interrupt URBs additionally run through periodic bandwidth placement before qTDs are linked.

Interrupt flow starts at the top-level `oxu_irq`, which masks chip-level interrupts, dispatches to `oxu210_hcd_irq` for the active logical controller, then restores the top-level mask. The EHCI IRQ handler clears status, handles INT/ERR completions, async advance, port-change wakeups, and fatal errors, then calls `ehci_work`. `ehci_work` drains async reclaim, scans async QHs, scans periodic entries if enabled, and arms the watchdog when work remains.

## State and Persistence Behavior
All persistent runtime state is in `struct oxu_hcd` and the USB core's endpoint/URB fields. Endpoint state persists through `urb->ep->hcpriv` QH pointers, URBs reference QHs through `urb->hcpriv`, and the async/periodic hardware-visible lists live in OXU on-chip memory. `qh_used`, `qtd_used`, `db_used`, and `murb_used` are bitmap-like allocation ledgers protected by `mem_lock`; schedule state is protected by `lock`.

The driver does not persist data outside kernel memory or device registers. Across suspend/resume it saves command/schedule intent in `oxu->command`, `bus_suspended`, `reset_done`, and the existing software schedule lists, then rewrites operational registers on resume. Across remove, all HCD state is destroyed through USB core removal and local cleanup.

## Dependencies and Integration Points
This file depends on the Linux USB HCD core, platform-device resources, IRQ APIs, MMIO helpers, DMA address assumptions, timers, spinlocks, and USB hub-control semantics. It is heavily derived from EHCI concepts but is self-contained rather than using the generic EHCI HCD implementation. It integrates with root hub polling through `usb_hcd_poll_rh_status`, remote wake through `usb_hcd_resume_root_hub`, HCD death through `usb_hc_died`, and URB completion through `usb_hcd_giveback_urb`.

The hardware-specific integration points are OXU top registers such as `OXU_HOSTIFCONFIG`, `OXU_SOFTRESET`, `OXU_CHIPIRQSTATUS`, `OXU_CHIPIRQEN_SET/CLR`, `OXU_CLKCTRL_SET`, `OXU_ASO`, and per-core `OXU_USBMODE`. Module parameters `log2_irq_thresh`, `park`, and `ignore_oc` affect interrupt latency, async park behavior, and root-hub overcurrent reporting.

## Risks
The largest risk is resource exhaustion in tiny fixed pools: 16 QHs, 32 qTDs, 8 data buffers, and 8 micro URBs. Submission paths sometimes busy-wait with `schedule()` until resources become available, which can hide pressure and risks latency or livelock if completions stop. Bulk URB splitting relies on `complete == NULL` to distinguish internal fragments, so unusual URB initialization or future USB core assumptions could break fragment completion.

The on-chip buffer allocator does manual power-of-two block allocation and computes physical addresses with `virt_to_phys` on MMIO-backed memory. That is hardware-specific and fragile if memory attributes or DMA addressing assumptions change. Isochronous support returns `-ENOSYS`, so callers expecting full EHCI feature parity will fail for iso endpoints. Endpoint disable intentionally leaks a QH rather than freeing it when the core did not unlink URBs first, which protects correctness but is a recoverability risk.

Concurrency is complex: completion callbacks drop and reacquire `oxu->lock`, scans can modify schedules during callbacks, async reclaim is watchdog-backed, and the top-level IRQ temporarily masks shared chip interrupts. Regressions around QH state transitions (`LINKED`, `UNLINK`, `IDLE`, `COMPLETING`, `UNLINK_WAIT`) can lead to use-after-free, leaked references, or wedged schedules. Root-hub control manually manages reset/resume timing and port R/WC bits; incorrect writes can lose change notifications or leave ports in reset/resume.

## Test Signals
Compile coverage should include `CONFIG_USB`, platform bus support, and this driver enabled, with warnings checked around pointer arithmetic on `void *`, `__iomem`, and DMA addresses. Runtime signals include successful probe showing OXU device ID and both OTG/SPH HCDs added, USB 2.0 devices enumerating on both logical controllers, bulk transfers above and below 4096 bytes completing with correct byte counts, interrupt devices maintaining periodic schedule bandwidth, and iso submissions returning the expected `-ENOSYS`.

Stress tests should force QH/qTD/buffer exhaustion with concurrent bulk and interrupt endpoints, test unlink while transfers are active, repeatedly disable endpoints, suspend/resume with remote wake enabled, and verify watchdog recovery when async-advance IRQs are delayed. Hub tests should cover reset completion, suspend/resume change bits, overcurrent behavior with and without `ignore_oc`, and remove/shutdown paths leaving no active IRQ or timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/oxu210hp-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/pci-quirks.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/pci-quirks.c

## Purpose
This file provides early and runtime USB PCI host-controller quirks for Linux. It resets or hands off UHCI, OHCI, EHCI, and xHCI controllers from firmware to the OS, handles Intel xHCI port routing, applies ASMedia flow-control tuning, and exposes AMD chipset helpers used by USB HCDs to avoid known power-management, prefetch, PLL, and disabled-port issues.

## Important APIs, Types, and Functions
The AMD-specific section, gated by `CONFIG_USB_PCI_AMD`, defines `enum amd_chipset_gen`, `struct amd_chipset_type`, and the global `amd_chipset` cache protected by `amd_lock`. Exported AMD helpers include `sb800_prefetch`, `usb_hcd_amd_remote_wakeup_quirk`, `usb_amd_hang_symptom_quirk`, `usb_amd_prefetch_quirk`, `usb_amd_quirk_pll_check`, `usb_amd_quirk_pll_disable`, `usb_amd_quirk_pll_enable`, `usb_amd_dev_put`, and `usb_amd_pt_check_port`.

Generic exported helpers include `usb_asmedia_modifyflowcontrol`, `uhci_reset_hc`, `uhci_check_and_reset_hc`, `usb_enable_intel_xhci_ports`, and `usb_disable_xhci_ports`. Internal handoff paths include `quirk_usb_handoff_uhci`, `quirk_usb_handoff_ohci`, `ehci_bios_handoff`, `quirk_usb_disable_ehci`, `handshake`, `quirk_usb_handoff_xhci`, and `quirk_usb_early_handoff`.

## Control Flow
The early handoff path is registered with `DECLARE_PCI_FIXUP_CLASS_FINAL` for USB-class PCI devices. `quirk_usb_early_handoff` filters unsupported devices, skips special Netlogic and Raspberry Pi 4 xHCI cases, enables the PCI device, dispatches by controller class, then disables the PCI device again.

UHCI handoff checks I/O BAR availability and resets legacy support, interrupts, and command state. OHCI handoff ioremaps BAR0, optionally requests ownership from firmware, disables interrupts, preserves `HcFmInterval` except for a known ULi lockup device, resets, and unmaps. EHCI handoff walks extended capabilities, performs BIOS semaphore handoff with DMI skip rules for broken systems, disables legacy SMIs, clears CONFIGFLAG when firmware previously owned the controller, then halts the controller and disables interrupts. xHCI handoff locates the xHCI legacy support extended capability, requests OS ownership, disables legacy SMIs, applies Intel port routing if appropriate, waits for controller readiness, and halts the controller with interrupts disabled.

AMD helper flow lazily initializes chipset identity with `usb_amd_find_chipset_info`. It probes SMBus and northbridge devices, records generation/revision, decides whether PLL quirks are needed, and holds PCI device references until `usb_amd_dev_put`. PLL disable/enable is reference-counted through `amd_chipset.isoc_reqs`, so multiple isochronous users keep the workaround active until the last release.

## State and Persistence Behavior
The only durable in-kernel state is the static `amd_chipset` cache. It stores referenced PCI devices, chipset generation/revision, northbridge type, `probe_count`, `isoc_reqs`, and whether the PLL quirk is required. `amd_lock` protects updates and reference-count transitions, while `pci_dev_put` is intentionally performed outside the spinlock.

Controller handoff functions persist changes in PCI config space and MMIO registers, including firmware ownership semaphores, interrupt masks, port-routing registers, and controller run/reset bits. There is no filesystem persistence.

## Dependencies and Integration Points
This code depends on PCI config access, I/O port access when UHCI is enabled, MMIO mapping, DMI, ACPI/OF device data, xHCI extended-capability definitions from `xhci-ext-caps.h`, and Linux PCI fixup infrastructure. It integrates with UHCI/OHCI/EHCI/xHCI host drivers by preparing controllers before normal probing and by exporting helper symbols that those drivers can call for chipset-specific behavior.

Intel routing uses PCI config registers `USB_INTEL_XUSB2PR`, `USB_INTEL_USB2PRM`, `USB_INTEL_USB3_PSSEN`, and `USB_INTEL_USB3PRM`. ASMedia flow control writes vendor-specific registers `ASMT_DATA_WRITE0/1`, `ASMT_CONTROL_REG`, and command/data constants.

## Risks
This file writes low-level chipset registers very early in boot, so bad detection can hang hardware, break firmware handoff, or disconnect boot-critical USB devices. Many paths are hardware-specific and depend on vendor/device/revision IDs and DMI strings staying accurate. The AMD PLL path manipulates southbridge and northbridge registers under a spinlock and uses I/O port cycles; incorrect reference counting could leave power management disabled or re-enable it while isochronous transfers are active.

The EHCI capability walker bounds the loop, but malformed config-space capabilities can still produce warnings or incomplete handoff. xHCI handoff assumes BAR0 length is sufficient before reading ext-cap registers and includes force-handoff exceptions for known devices. Intel port switchover must not run when xHCI support is missing, or USB ports may become unusable; the code explicitly disables xHCI routing in that configuration.

## Test Signals
Build signals should cover combinations of `CONFIG_USB_PCI`, `CONFIG_USB_PCI_AMD`, `CONFIG_USB_UHCI_HCD`, `CONFIG_HAS_IOPORT`, `CONFIG_USB_XHCI_HCD`, DMI, OF, and ACPI. Runtime validation includes early boot logs for BIOS handoff failures, no hangs on known DMI skip systems, successful UHCI/OHCI/EHCI/xHCI probing after fixups, Intel switchable USB2/USB3 ports routing to xHCI only when supported, and ASMedia writes completing without timeout.

AMD-specific tests should verify chipset detection reference counts, `usb_amd_dev_put` cleanup, PLL disable/enable nesting under concurrent isochronous streams, SB800 prefetch toggling, Promontory disabled-port detection for supported device IDs, and remote-wakeup/hang/prefetch quirk decisions on matching revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/pci-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/pci-quirks.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/pci-quirks.h

## Purpose
This header declares the USB PCI quirk helpers implemented in `pci-quirks.c` and provides safe inline no-op or false-returning stubs when the relevant configuration options are disabled. It lets USB host-controller drivers call chipset and handoff helpers without scattering preprocessor conditionals through their own implementations.

## Important APIs, Types, and Functions
Under `CONFIG_USB_PCI_AMD`, the header declares AMD helpers: `usb_hcd_amd_remote_wakeup_quirk`, `usb_amd_hang_symptom_quirk`, `usb_amd_prefetch_quirk`, `usb_amd_dev_put`, `usb_amd_quirk_pll_check`, `usb_amd_quirk_pll_disable`, `usb_amd_quirk_pll_enable`, `sb800_prefetch`, and `usb_amd_pt_check_port`. When disabled, the stubs return `false` for boolean queries and do nothing for mutators.

Under `CONFIG_USB_PCI`, it declares UHCI reset helpers, ASMedia flow-control tuning, Intel xHCI routing enable, and xHCI port disable helpers. When disabled, only stubs for `usb_asmedia_modifyflowcontrol` and `usb_disable_xhci_ports` are provided; the UHCI and Intel enable declarations are absent because callers should only require them when PCI USB support is built.

## Control Flow
There is no runtime control flow beyond inline stub execution. The compile-time control flow is determined by `CONFIG_USB_PCI_AMD` and `CONFIG_USB_PCI`. Enabled configurations bind callers to exported symbols from `pci-quirks.c`; disabled configurations compile no-op paths directly into callers.

## State and Persistence Behavior
The header owns no state. Its stubs intentionally do not allocate, retain, or release anything. In enabled AMD builds, callers must still pair chipset initialization side effects with `usb_amd_dev_put` according to the implementation contract in `pci-quirks.c`.

## Dependencies and Integration Points
The declarations depend on Linux PCI and device model types (`struct pci_dev`, `struct device`) but forward-declare `struct pci_dev` in the non-PCI branch to avoid unnecessary include coupling. The header is consumed by USB host-controller drivers and the PCI quirks implementation itself.

## Risks
The main risk is configuration mismatch. A caller that assumes a helper has real behavior in a disabled configuration will silently get a no-op or `false`, so feature behavior must be guarded by the same configuration semantics. The absence of some stubs in the non-`CONFIG_USB_PCI` branch means misuse can surface as compile errors, which is preferable for helpers that are not meaningful without PCI support.

## Test Signals
Compile matrix testing is the key signal: build with AMD quirks enabled/disabled, PCI USB enabled/disabled, and with host drivers that include this header. Functional tests should confirm disabled configurations do not require unresolved symbols, while enabled configurations link to the `EXPORT_SYMBOL_GPL` definitions in `pci-quirks.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/pci-quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/r8a66597-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/r8a66597-hcd.c

## Purpose
This file implements the Renesas R8A66597 USB host-controller driver. It provides platform-driver probe/remove, USB HCD callbacks, hardware initialization, root-hub emulation, endpoint pipe allocation, FIFO transfer handling, interrupt dispatch, timers, and power-management support for on-chip and external R8A66597 variants.

## Important APIs, Types, and Functions
The primary integration point is `r8a66597_hc_driver`, whose callbacks include `r8a66597_start`, `r8a66597_stop`, `r8a66597_urb_enqueue`, `r8a66597_urb_dequeue`, `r8a66597_endpoint_disable`, `r8a66597_get_frame`, `r8a66597_hub_status_data`, `r8a66597_hub_control`, and optional bus suspend/resume. Platform entry points are `r8a66597_probe` and `r8a66597_remove`, registered with `module_platform_driver`.

Transfer state is represented by `struct r8a66597_td` and `struct r8a66597_pipe` from `r8a66597.h`. Important local helpers include `enable_controller`, `disable_controller`, `r8a66597_clock_enable`, `r8a66597_enable_port`, `alloc_usb_address`, `free_usb_address`, `init_pipe_info`, `enable_r8a66597_pipe`, `pipe_setting`, `start_transfer`, `finish_request`, `packet_read`, `packet_write`, `irq_pipe_ready`, `irq_pipe_empty`, `irq_pipe_nrdy`, and `r8a66597_irq`.

## Control Flow
Probe obtains MMIO and IRQ resources, validates platform data, creates a USB HCD, initializes private state, obtains a clock for on-chip variants, disables pending controller state, initializes per-pipe queues and timers, and calls `usb_add_hcd`. HCD start enables clocks, configures pin/USB/endian/interrupt registers, enables root ports, and sets the HCD running. Stop disables interrupts, clears status, disables ports, and shuts down clocks.

URB enqueue runs under `r8a66597->lock`, links the URB to the USB core endpoint, lazily allocates endpoint pipe state, initializes pipe configuration, creates a TD, queues it on the per-pipe queue, and either starts the transfer immediately or arms interval/timeout timers. Control transfers run through setup, data, and status phases via `check_next_phase`; bulk/interrupt/isoc transfers use direct IN/OUT packet preparation. Completion removes the TD, saves toggle state, gives the URB back outside the spinlock, and restarts the next queued TD for the pipe.

The IRQ handler reads and masks INTSTS/INTENB registers for both root ports and transfer events. Attach/detach starts root-hub sampling or disconnect cleanup. SACK/SIGN complete control setup phases. BRDY, BEMP, and NRDY dispatch to FIFO read/write, empty completion, and error completion paths. Timers handle root-hub line-state debounce, interval scheduling, and TD timeout rotation.

## State and Persistence Behavior
Persistent runtime state lives in `struct r8a66597`: MMIO base, clock, platform data, root-hub port status, per-pipe TD queues, timers, address maps, timeout/interval maps, pipe usage counts, DMA-channel use, child-device list, child-connect bitmap, and bus-suspend flag. USB device state is mirrored in `struct r8a66597_device`, attached to `struct usb_device` via driver data after address assignment.

The driver maintains a hardware address map separate from USB device addresses and programs `DEVADDn` registers with speed, parent hub, hub port, and root port. Endpoint toggles are stored in per-device bitmaps and restored when a pipe is reused. There is no filesystem persistence; hardware register state is rebuilt after probe and resume.

## Dependencies and Integration Points
The driver depends on Linux USB HCD APIs, platform resources, Renesas platform data from `<linux/usb/r8a66597.h>`, MMIO helpers from `r8a66597.h`, timers, IRQ APIs, cache flushing for IN transfers, and optional clock framework support for on-chip controllers. It integrates with root-hub polling/status callbacks, `usb_hcd_link_urb_to_ep`, `usb_hcd_unlink_urb_from_ep`, `usb_hcd_giveback_urb`, `usb_root_hub_lost_power`, and global USB bus child enumeration for child disconnect detection.

Hardware integration is register-level: SYSCFG, DVSTCTR, INTENB/INTSTS, FIFO select/control, pipe configuration, pipe transaction counters, and DEVADD registers are manipulated directly. Platform data controls endian mode, VIF, on-chip behavior, clock selection, port power callback, and external-bus write quirks.

## Risks
The driver manually owns USB address allocation, child-device lifetime, endpoint pipe sharing, FIFO selection, and toggle persistence. Bugs in disconnect, reset, or child-hub tracking can leave stale device pointers or leaked pipe counts. `free_usb_address` comments acknowledge that USB device memory may already be freed during disconnect, so reset-sensitive driver-data clearing must remain carefully constrained.

Concurrency is delicate: many helpers require interrupts disabled and run under the main spinlock, while URB giveback and root-hub polling intentionally drop the lock. TD timers can rotate queued TDs when no progress is observed, which risks fairness or incorrect reordering if endpoint/address comparisons are wrong. Pipe/FIFO register selection must be serialized correctly to avoid data corruption across endpoints.

Feature limitations and hardware quirks are also visible: only 10 hardware device addresses are available, external hub depth is limited by `is_hub_limit`, DMA FIFO use is constrained to two channels and not available on-chip, and port sampling depends on repeated stable line-state reads. PM paths disable and re-enable the controller and report root-hub power loss, so devices should be expected to re-enumerate.

## Test Signals
Build signals include platform-driver compilation with and without `CONFIG_PM`, on-chip clock support, and the Renesas platform-data header. Runtime tests should cover probe/remove, one-root-hub on-chip and two-root-hub external variants, low/full/high-speed enumeration, set-address handling, hub depth limit behavior, bulk/interrupt/control transfers in both directions, zero-length and short packets, isochronous packet accounting, endpoint disable, URB unlink, and disconnect during active transfers.

Stress tests should exercise all hardware pipes, DMA channel allocation/release, repeated resets, child hub connect/disconnect maps, root-hub debounce, suspend/resume with remote wake, and timeout timer behavior under stalled or NAKing devices. Useful failure signals are `register ... timeout`, FIFO not ready messages, illegal pipe/root-port logs, leaked device drvdata, or URBs not completing after disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/r8a66597-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/r8a66597.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/r8a66597.h

## Purpose
This header defines the private data structures and inline register/FIFO helpers used by the R8A66597 host-controller driver. It bridges platform data and hardware register definitions from `<linux/usb/r8a66597.h>` with the HCD implementation in `r8a66597-hcd.c`.

## Important APIs, Types, and Functions
The main types are `struct r8a66597_pipe_info`, `struct r8a66597_pipe`, `struct r8a66597_td`, `struct r8a66597_device`, `struct r8a66597_root_hub`, `struct r8a66597_timers`, and `struct r8a66597`. Together they represent endpoint pipe configuration, queued transfer descriptors, per-device hardware address/toggle state, root-hub port state, per-pipe timers, and controller-global state.

Important inline helpers include `hcd_to_r8a66597`, `r8a66597_to_hcd`, `r8a66597_get_td`, `r8a66597_get_urb`, `r8a66597_read`, `r8a66597_write`, `r8a66597_mdfy`, `r8a66597_read_fifo`, `r8a66597_write_fifo`, register selector helpers for per-port and per-pipe registers, `get_rh_usb_speed`, `r8a66597_port_power`, and `get_xtal_from_pdata`. Macros classify pipe ranges, build device selectors, and enable/disable BRDY/BEMP/NRDY interrupt bits through implementation-provided `enable_pipe_irq` and `disable_pipe_irq`.

## Control Flow
The header has no standalone control flow, but its inlines are on the hot path for every HCD operation. FIFO read/write helpers branch on `pdata->on_chip` to use 32-bit accesses for on-chip controllers and 16-bit accesses for external controllers. Odd-byte writes on external hardware optionally toggle `MBW_16` around an 8-bit write when `wr0_shorted_to_wr1` is set. Port power either delegates to `pdata->port_power` or directly toggles the `VBOUT` bit.

## State and Persistence Behavior
The structures declared here define the driver's persistent in-memory state. `struct r8a66597` owns the lock, MMIO base, optional clock, platform data, default device zero, root hubs, per-pipe queues, root-hub and pipe timers, address/timeout/interval maps, pipe/DMA maps, child-device list, child-connect map, and suspend flags. `struct r8a66597_device` persists per USB device until disconnect/reset and stores hardware address, USB address, endpoint toggles, pipe counts, DMA ownership, and device-list membership.

The header itself does not persist external data. It provides helpers that persist state into hardware registers through MMIO writes when called by the C file.

## Dependencies and Integration Points
This file depends on `<linux/clk.h>` and `<linux/usb/r8a66597.h>` for clock and register/platform definitions, and on USB core/HCD types included by the implementation. It is tightly coupled to `r8a66597-hcd.c`, which supplies interrupt-enable functions referenced by macros and uses every structure here as private HCD state.

The IO helpers integrate directly with Linux `ioread16`, `ioread32_rep`, `iowrite16`, `iowrite32_rep`, and `iowrite8`. Endianness, bus width, clock source, and power control behavior are delegated to platform data, making board descriptions part of the driver's effective behavior.

## Risks
Because these are inline hardware accessors, mistakes propagate broadly. The FIFO helpers perform pointer arithmetic on MMIO addresses and copy partial 32-bit words into caller buffers; off-by-one lengths or wrong platform flags can corrupt transfer data. The external odd-byte write path changes FIFO bus width around a byte write, so missing restoration would affect subsequent transfers.

Several macros assume valid pipe numbers and port indexes. Callers must enforce bounds for `pipe_queue`, root-hub arrays, and register selector helpers. `get_xtal_from_pdata` only logs invalid clock selection and returns zero, so bad platform data may fail later in less obvious register setup.

## Test Signals
Compile testing should verify this header with the R8A66597 driver across on-chip and external platform-data configurations. Runtime signals include correct FIFO data for aligned and odd-length transfers, correct behavior in big-endian mode, working board-specific `port_power`, correct root-hub speed decoding, and stable interrupt masking through the BRDY/BEMP/NRDY macros. Static analysis should focus on array bounds, MMIO pointer arithmetic, and assumptions that `enable_pipe_irq`/`disable_pipe_irq` are visible before macro expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/r8a66597.h -->
