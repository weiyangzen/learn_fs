# subset-b-005476 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-trace.h

Purpose: defines Linux tracepoints for the Cadence CDNSP gadget-side controller, covering endpoint state, control requests, TRBs, rings, contexts, requests, port status, streams, bounce buffers, and miscellaneous lifecycle messages.

Important APIs/types/functions: declares `TRACE_SYSTEM cdnsp-dev`, `CDNSP_MSG_MAX`, multiple `DECLARE_EVENT_CLASS` blocks, and concrete events such as `cdnsp_tr_drbl`, `cdnsp_handle_event`, `cdnsp_request_enqueue`, `cdnsp_ep_disabled`, `cdnsp_ring_alloc`, `cdnsp_handle_port_status`, and `cdnsp_stream_number`. It depends on CDNSP gadget/debug helpers such as `cdnsp_decode_trb`, `cdnsp_trb_virt_to_dma`, and USB decode helpers.

Control flow: this header has no runtime control flow of its own; compile-time tracepoint macros generate event call sites and formatters. Fast-assign blocks snapshot selected object fields before `TP_printk` decodes them for ftrace consumers.

State and persistence: trace events persist only in kernel tracing buffers. They snapshot DMA addresses, request metadata, ring pointers, stream counters, and context words but do not own controller state.

Dependencies and integration: included by CDNSP gadget implementation files with `CREATE_TRACE_POINTS` in one translation unit. The trailing `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` block is required by the kernel tracepoint build system.

Risks: tracepoint formatters dereference nested objects passed by callers, so call sites must pass valid endpoint, ring, request, context, and state pointers. Large decode strings are bounded by `CDNSP_MSG_MAX`; very detailed TRBs or control requests may be truncated.

Test signals: useful validation comes from enabling ftrace events under the `cdnsp-dev` system during enumeration, endpoint enable/disable, transfer completion, stream setup, and port-status changes; build coverage must ensure the generated trace header compiles exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/core.c

Purpose: implements the Cadence USBSS/CDNSP dual-role core orchestration layer, selecting host/device/idle roles, registering optional USB role-switch support, wiring wakeup IRQs, and exporting probe/remove/suspend/resume helpers for glue drivers.

Important APIs/types/functions: exports `cdns_init`, `cdns_remove`, `cdns_suspend`, `cdns_resume`, and `cdns_set_active`. Internal role helpers include `cdns_role_start`, `cdns_role_stop`, `cdns_core_init_role`, `cdns_hw_role_state_machine`, `cdns_hw_role_switch`, `cdns_role_get`, `cdns_role_set`, and `cdns_wakeup_irq`.

Control flow: `cdns_init` sets a 32-bit DMA mask, initializes locking, registers `usb_role_switch` when firmware exposes `usb-role-switch`, installs the wakeup IRQ, initializes DRD registers, initializes role drivers based on firmware mode, Kconfig, and strap mode, then starts idle plus the selected role. Hardware-driven OTG uses ID/VBUS state to move `NONE -> HOST`, `NONE -> DEVICE`, and back through `NONE`. Role-switch class control bypasses hardware switching.

State and persistence: persistent state lives in `struct cdns`: current `role`, `dr_mode`, role-driver slots and states, wakeup flags, PM state, child host/gadget devices, PHY pointers, and DRD register mappings. State survives until remove and is restored after power loss by `cdns_resume`.

Dependencies and integration: integrates with `drd.c` for register mode control, `host.c` for xHCI child creation, gadget init callbacks from controller-specific code, runtime PM, system PM, USB role-switch class, and PHY reset on idle stop.

Risks: mode negotiation can fail if firmware `dr_mode`, strap state, and enabled Kconfig roles disagree. `pm_runtime_get_sync` return values are not checked. Role transitions are mutex-guarded, but IRQ and PM paths must preserve valid `cdns->role` indices and role callbacks.

Test signals: probe logs, role-switch sysfs/user-space changes, ID/VBUS interrupts, wakeup IRQ resume, suspend/resume with power loss, and host/device-only configurations are the key validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/core.h -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/core.h

Purpose: defines the shared Cadence USBSS/CDNSP core data model and exported core lifecycle APIs used by DRD, host, gadget, and platform glue code.

Important APIs/types/functions: declares `struct cdns_role_driver`, `struct cdns3_platform_data`, `struct cdns`, controller version constants, platform quirk bits, `CDNS_XHCI_RESOURCES_NUM`, and prototypes for `cdns_hw_role_switch`, `cdns_init`, `cdns_remove`, and PM helpers.

Control flow: no executable flow beyond PM stubs when `CONFIG_PM_SLEEP` is disabled. The header defines the callback contract that `core.c` invokes for each role: `start`, `stop`, `suspend`, and `resume`.

State and persistence: `struct cdns` is the persistent controller object. It stores MMIO mappings for xHCI/device/OTG variants, IRQs, role driver table, current role, child devices, PHYs, role switch, low-power/wakeup flags, platform data, spinlock/mutex, xHCI private data, APB timeout override, and gadget init callback.

Dependencies and integration: depends on USB OTG and USB role headers and is included across cdns3 DRD/host/gadget code. Glue drivers fill resources and platform data before calling `cdns_init`.

Risks: the struct mixes fields for three controller generations; code must select the right register pointer according to `version`. Role-array indexing assumes Linux `enum usb_role` values up to `USB_ROLE_DEVICE`.

Test signals: compile coverage across host-only, gadget-only, OTG, and PM-disabled builds confirms callback stubs and struct users remain consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/drd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/drd.c

Purpose: implements Cadence DRD/OTG register access, controller-version detection, mode programming, OTG interrupt handling, host/device bus request sequencing, VBUS override controls, PHY mode changes, and power-loss detection.

Important APIs/types/functions: exports `cdns_get_id`, `cdns_get_vbus`, `cdns_clear_vbus`, `cdns_set_vbus`, `cdns_is_host`, `cdns_is_device`, `cdns_drd_host_on/off`, `cdns_drd_gadget_on/off`, `cdns_drd_update_mode`, `cdns_drd_init`, `cdns_drd_exit`, and `cdns_power_is_lost`. Key internals are `cdns_set_mode`, `cdns_init_otg_mode`, `cdns_drd_irq`, and `cdns_drd_thread_irq`.

Control flow: `cdns_drd_init` maps OTG registers, detects v0/v1/CDNSP via first register and DID patterns, initializes version-specific register pointers, applies suspend-residency quirks, reads strap mode, registers a threaded OTG IRQ, and verifies readiness. Mode updates call `cdns_set_mode`; OTG mode enables ID/VBUS interrupts. IRQ top-half filters OTG events, clears interrupt vectors, and wakes the thread, which calls `cdns_hw_role_switch`.

State and persistence: persistent state is written into `struct cdns` register pointers, `version`, `dr_mode`, and PHY modes. Hardware state persists in OTG command/status/override/simulate registers until reset or power loss.

Dependencies and integration: integrates with `core.c` role switching, Linux PHY API, MMIO polling helpers, and controller-specific register layouts from `drd.h`.

Risks: readiness waits can timeout; incorrect DID/strap interpretation prevents probe. VBUS override helpers are CDNSP-only no-ops elsewhere. IRQ handling ignores events in low-power mode, so PM wakeup paths must resume before role switching.

Test signals: validate v0/v1/CDNSP probe, strap-limited host/peripheral modes, OTG ID/VBUS transitions, host/device ready-bit timeouts, PHY mode changes, and resume after simulated power loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/drd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/drd.h -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/drd.h

Purpose: describes Cadence DRD/OTG MMIO layouts for CDNS3 v0, CDNS3 v1, and CDNSP v2 and provides all command/status/interrupt/override bit definitions used by the DRD implementation.

Important APIs/types/functions: defines `struct cdns3_otg_regs`, `struct cdns3_otg_legacy_regs`, `struct cdnsp_otg_regs`, `struct cdns_otg_common_regs`, `struct cdns_otg_irq_regs`, DID detection macros, OTG command/status/interrupt masks, strap values, ready bits, override bits, and declarations for DRD helper functions.

Control flow: no executable flow; the header encodes register addressing and bit semantics consumed by `drd.c` and role code.

State and persistence: register structs mirror persistent hardware state such as command, status, OTG state, interrupt enable/vector, simulate, override, suspend control, and PHY reset configuration registers.

Dependencies and integration: includes Linux OTG definitions and `core.h`; it is the ABI-like internal contract between generic cdns3 core and generation-specific OTG register maps.

Risks: v0/v1/v2 register offsets differ; using the wrong struct for a detected version would corrupt unrelated registers. Some strap and ready bit meanings differ for CDNSP, requiring the version checks used in `drd.c`.

Test signals: compile-time consumers plus hardware probe on each controller generation, especially CDNSP ready-bit inversion and v0 ID-pullup override, are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/drd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/gadget-export.h -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/gadget-export.h

Purpose: provides conditional gadget initialization declarations for CDNSP and CDNS3 gadget roles, returning `-ENXIO` stubs when the relevant gadget support is not built.

Important APIs/types/functions: declares or stubs `cdnsp_gadget_init(struct cdns *)` under `CONFIG_USB_CDNSP_GADGET` and `cdns3_gadget_init(struct cdns *)` under `CONFIG_USB_CDNS3_GADGET`.

Control flow: no runtime flow beyond inline fallback stubs. Callers can unconditionally reference these helpers and receive a normal error if a role is disabled.

State and persistence: no owned state. Successful real implementations populate `struct cdns` gadget role fields outside this header.

Dependencies and integration: included by Cadence platform/core files that select the correct gadget initializer based on controller generation and Kconfig.

Risks: build-symbol naming must match Kconfig; a disabled gadget role appears as `-ENXIO`, so probe/mode negotiation must treat that as unsupported rather than hardware failure.

Test signals: host-only, gadget-only, and OTG build matrices verify the inline stubs and declarations line up with compiled implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/gadget-export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/host-export.h -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/host-export.h

Purpose: exposes the Cadence host-role initializer to core code when host support is enabled and provides an inline `-ENXIO` fallback otherwise.

Important APIs/types/functions: declares `cdns_host_init(struct cdns *)` under `CONFIG_USB_CDNS_HOST`; otherwise defines an inline `cdns_host_init` returning `-ENXIO` and an empty `cdns_host_exit` stub.

Control flow: no runtime control beyond the fallback return path. It lets `core.c` compile and report unsupported host role when Kconfig excludes host support.

State and persistence: no owned state. The real host initializer fills `cdns->roles[USB_ROLE_HOST]`.

Dependencies and integration: included by `core.c` and `host.c` to bridge the role framework to xHCI platform-device creation.

Risks: the guard macro uses `CONFIG_USB_CDNS_HOST`, while core mode checks distinguish CDNS3/CDNSP host configs; Kconfig consistency is required to avoid unexpected `-ENXIO`.

Test signals: build host-disabled and host-enabled variants and verify OTG/host-only probes reject unsupported host mode gracefully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/host-export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/host.c -->
# sources/distributed-fs/ceph-client/drivers/usb/cdns3/host.c

Purpose: implements the Cadence host role by powering the DRD block into host mode and registering an `xhci-hcd` child platform device with Cadence-specific xHCI quirks.

Important APIs/types/functions: main role callbacks are `__cdns_host_init`, `cdns_host_exit`, and `cdns_host_resume`; public initializer is `cdns_host_init`. xHCI platform private data includes `xhci_cdns3_plat_start`, `xhci_cdns3_resume_quirk`, `xhci_plat_cdns3_xhci`, and `xhci_plat_cdnsp_xhci`.

Control flow: role start calls `cdns_drd_host_on`, allocates `xhci-hcd`, attaches xHCI MMIO/IRQ resources, chooses CDNS3 or CDNSP quirks, optionally allows default runtime PM, registers the child device, and caches xHCI regs from the resulting HCD. Stop unregisters the child, frees private data, clears `host_dev`, and powers host mode off.

State and persistence: stores host child device in `cdns->host_dev`, xHCI private data in `cdns->xhci_plat_data`, and xHCI register base in `cdns->xhci_regs`. Resume marks xHCI `power_lost`.

Dependencies and integration: depends on `drd.c` host on/off, Linux platform-device APIs, xHCI platform driver internals, and xHCI register definitions.

Risks: if `platform_device_add` fails, private data and child device cleanup must remain balanced. `cdns_drd_host_on` return is not checked in `__cdns_host_init`, so later xHCI setup may expose earlier mode-on failures indirectly.

Test signals: host role probe, xHCI child enumeration, runtime PM resume quirk, CDNSP-specific context quirk, host stop/restart during OTG switches, and failure injection around child registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/cdns3/host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/Kconfig

Purpose: defines the build-time configuration surface for the ChipIdea Highspeed Dual Role Controller core, optional host/device roles, and platform glue drivers.

Important APIs/types/functions: declares `USB_CHIPIDEA`, `USB_CHIPIDEA_UDC`, `USB_CHIPIDEA_HOST`, and glue options for PCI, MSM, NPCM, i.MX, generic USB2, and Tegra. The core selects dependencies such as `EXTCON`, `RESET_CONTROLLER`, `USB_ULPI_BUS`, and `USB_ROLE_SWITCH`.

Control flow: Kconfig selections control which objects `Makefile` compiles and which inline stubs are active in headers such as `host.h` and `otg_fsm.h`.

State and persistence: no runtime state. Configuration persists in the kernel `.config` and determines available roles and glue modules.

Dependencies and integration: requires DMA and either EHCI host or USB gadget support. Host role depends on `USB_EHCI_HCD`; gadget role depends on `USB_GADGET`; several glue options depend on OF or PCI.

Risks: selecting dual-role core without matching role options can still build a core that rejects unsupported runtime modes. Defaults tie glue drivers to `USB_CHIPIDEA`, which can broaden build coverage unexpectedly for expert configurations.

Test signals: randconfig/allmodconfig builds and explicit host-only, gadget-only, OTG, PCI, OF, and Tegra/i.MX configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/Makefile

Purpose: maps ChipIdea Kconfig symbols to core, role, trace, OTG FSM, and glue driver objects.

Important APIs/types/functions: builds `ci_hdrc.o` from `core.o otg.o debug.o ulpi.o`, conditionally adds `udc.o trace.o`, `host.o`, and `otg_fsm.o`, and emits glue modules `ci_hdrc_usb2.o`, `ci_hdrc_msm.o`, `ci_hdrc_npcm.o`, `ci_hdrc_pci.o`, `usbmisc_imx.o ci_hdrc_imx.o`, and `ci_hdrc_tegra.o`.

Control flow: no runtime flow; object inclusion controls available callbacks and tracepoint definitions. `CFLAGS_trace.o := -I$(src)` supports `define_trace.h` finding `trace.h`.

State and persistence: no runtime state; build artifact composition is determined by Kconfig.

Dependencies and integration: ties the central `ci_hdrc` module to role implementations and platform glue modules. The i.MX rule also includes `usbmisc_imx.o`, an important sidecar dependency for `ci_hdrc_imx.c`.

Risks: trace builds require exactly one `CREATE_TRACE_POINTS` translation unit. Missing conditional objects surface as `-ENXIO` stubs or link errors depending on header coverage.

Test signals: build matrix across UDC, host, OTG FSM, and each glue driver; tracepoint build validates the special include flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/bits.h -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/bits.h

Purpose: centralizes ChipIdea register bit masks and field encodings for identification, capability, command/status, port, device link, OTG status/control, USB mode, and endpoint control registers.

Important APIs/types/functions: defines masks such as `DCCPARAMS_DC/HC`, `USBCMD_RS/RST`, `USBi_*`, `PORTSC_*`, `DEVLC_*`, `OTGSC_*`, `USBMODE_CM/DC/SDIS`, endpoint control masks, and PHY type encodings `PTS_UTMI`, `PTS_ULPI`, `PTS_SERIAL`, and `PTS_HSIC`.

Control flow: no executable flow. The macros feed `hw_read`, `hw_write`, OTG IRQ handling, PHY mode configuration, and host/gadget role code.

State and persistence: macros describe persistent hardware bits. Write-one-to-clear fields such as `PORTSC_W1C_BITS` and `OTGSC_INT_STATUS_BITS` are especially stateful at the hardware boundary.

Dependencies and integration: includes EHCI definitions and is shared by core, host, OTG, debug, and glue notify paths.

Risks: several fields are overloaded between LPM and non-LPM register maps; callers must choose `PORTSC` versus `DEVLC` based on `ci->hw_bank.lpm`. Incorrect write-one-to-clear masks can accidentally drop pending events.

Test signals: register-level hardware tests for mode reset, OTG interrupt clear/enable, port test mode, PHY interface selection, and endpoint enable/flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci.h -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci.h

Purpose: defines the common ChipIdea controller model, register map indices, role-driver interface, endpoint representation, MMIO helpers, role conversion helpers, and internal function prototypes.

Important APIs/types/functions: key types are `struct ci_hw_ep`, `enum ci_role`, `enum ci_revision`, `struct ci_role_driver`, `struct hw_bank`, and `struct ci_hdrc`. Important helpers include `ci_role`, `ci_role_start`, `ci_role_stop`, `ci_role_to_usb_role`, `usb_role_to_ci_role`, `hw_read_id_reg`, `hw_write_id_reg`, `hw_read`, `hw_write`, `hw_test_and_clear`, `hw_test_and_write`, and `ci_otg_is_fsm_mode`.

Control flow: inline role start validates role availability, invokes role callback, records `ci->role`, and signals legacy USB PHY events. Role stop marks `CI_ROLE_END`, invokes stop, and clears PHY events. MMIO helpers apply read-modify-write masks and optionally use the i.MX28 SWP write workaround.

State and persistence: `struct ci_hdrc` persists all controller state: locks, mapped register bank, IRQ, role table/current role, OTG FSM timers/workqueue, DMA pools, gadget endpoints and control transfer state, platform data, PHYs, HCD, extcon event flags, quirks, runtime PM flags, low-power flags, revision, and mutex.

Dependencies and integration: shared by core, host, gadget, OTG, debug, trace, and SoC glue code; bridges Linux gadget, host, OTG FSM, role-switch, ULPI, PHY, and platform data APIs.

Risks: `ci_role()` uses `BUG_ON` for invalid role state, so callers must guard role transitions carefully. Register helper masks use `~mask` semantics that assume nonzero masks. Shared state is protected by a mix of spinlock and mutex depending on IRQ versus role-switch context.

Test signals: compile all role combinations; exercise role transitions, register helpers on i.MX28 and normal MMIO paths, OTG FSM enablement, and PM paths touching `in_lpm` and wakeup flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_imx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_imx.c

Purpose: implements the i.MX/NXP/S32G ChipIdea glue driver, translating device-tree match data and USBMISC resources into `ci_hdrc_platform_data`, clocks, PHYs, pinctrl, regulators, wakeup IRQs, runtime PM, and SoC-specific notifications.

Important APIs/types/functions: defines SoC flag tables, `struct ci_hdrc_imx_data`, `usbmisc_get_init_data`, clock helpers, `ci_hdrc_imx_notify_event`, wakeup IRQ handler, probe/remove/shutdown, and system/runtime PM callbacks.

Control flow: probe reads match flags, parses `fsl,usbmisc`, configures HSIC pinctrl/regulator, optional PM QoS, clocks, wakeup clock, USB PHY phandles, ULPI override handling, wakeup IRQ, USBMISC init, then calls `ci_hdrc_add_device`. Post-init records external ID/VBUS and available role for USBMISC. Remove and error paths unwind child device, PHY override, clocks, QoS, and USBMISC device references.

State and persistence: persistent glue state includes child `ci_pdev`, clocks, wakeup IRQ, USBMISC data, HSIC regulator/pinctrl, runtime PM support, low-power flag, PM QoS request, and SoC flag pointer.

Dependencies and integration: integrates with USBMISC helper functions, OF properties, clocks, USB PHY, pinctrl, regulators, PM QoS, runtime PM, out-of-band wakeup, and the ChipIdea core platform-device API.

Risks: many optional resources have deferred-probe paths. Clock and QoS unwinding must stay balanced. Wakeup IRQ and parent/child runtime PM sequencing can race with core suspend. USBMISC reference handling depends on `put_device`.

Test signals: boot/probe on i.MX variants, HSIC active/suspend notifications, charger detection and pullup events, runtime/system suspend-resume with wakeup IRQ, ULPI override platforms, and device-tree extcon/role-switch combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_imx.h -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_imx.h

Purpose: declares the i.MX USBMISC data contract and helper APIs used by the i.MX ChipIdea glue driver.

Important APIs/types/functions: defines `struct imx_usbmisc_data` with device/index, over-current polarity, power polarity, external VBUS divider, ULPI/HSIC flags, external ID/VBUS flags, USB PHY, available role, and PHY tuning values. Declares `imx_usbmisc_init`, `imx_usbmisc_init_post`, `imx_usbmisc_hsic_set_connect`, `imx_usbmisc_charger_detection`, `imx_usbmisc_suspend`, `imx_usbmisc_resume`, and `imx_usbmisc_pullup`.

Control flow: no executable flow. The header supplies the typed interface between `ci_hdrc_imx.c` and USBMISC implementation files.

State and persistence: `imx_usbmisc_data` persists SoC-specific sideband configuration and is stored by the glue driver for notifications and PM.

Dependencies and integration: depends on USB PHY and USB role mode types through included users. It is included by both ChipIdea i.MX glue and USBMISC code.

Risks: bitfield names such as external ID/VBUS control hardware behavior indirectly; stale or incorrectly parsed data-tree properties can cause wrong wakeup, charger, or over-current behavior.

Test signals: compile with i.MX glue and USBMISC, validate DT parsing populates fields, and exercise USBMISC init/post/suspend/resume plus charger and pullup notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_imx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_msm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_msm.c

Purpose: implements Qualcomm MSM ChipIdea glue, including clocks, reset controller support for PHY POR reset, optional PHY muxing, HSIC detection, and controller reset notifications.

Important APIs/types/functions: defines `struct ci_hdrc_msm`, reset op `ci_hdrc_msm_por_reset`, notification callback `ci_hdrc_msm_notify_event`, PHY mux helper `ci_hdrc_msm_mux_phy`, and platform probe/remove.

Control flow: probe allocates glue state, fills platform data with shared-register, streaming-disable, AHB-burst, and override-phy-control quirks, obtains core/interface/optional FS clocks, maps vendor PHY registers, registers reset controller, pulses core reset, enables clocks, optionally selects secondary PHY through syscon, detects HSIC child PHY, and adds the `ci_hdrc` child. Reset notifications configure PHY mode, unclamp secondary PHY, initialize/power PHY, program AHB and workaround registers, and set session-valid override for extcon/role-switch.

State and persistence: stores child platform device, clocks, platform data, reset-controller device, secondary PHY and HSIC booleans, and vendor base MMIO.

Dependencies and integration: uses common clock, reset, syscon/regmap, OF child parsing, PHY APIs, PM runtime no-callback mode, and ChipIdea platform add/remove.

Risks: direct vendor register writes assume resource 1 mapping and correct PHY selection arguments. PHY init/power is tied to core reset/stop notifications rather than core-managed PHY control. FS clock is disabled after reset pulse and must tolerate optional absence.

Test signals: MSM probe/remove, reset-controller users, HSIC and non-HSIC PHY paths, extcon/role-switch session-valid override, and controller stop notification powering off PHY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_msm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_npcm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_npcm.c

Purpose: implements Nuvoton NPCM USB device-controller glue for ChipIdea, with optional core clock handling and device-mode platform quirks.

Important APIs/types/functions: defines `struct npcm_udc_data`, `npcm_udc_notify_event`, `npcm_udc_probe`, and `npcm_udc_remove`, plus OF matches for `nuvoton,npcm750-udc` and `nuvoton,npcm845-udc`.

Control flow: probe enables the optional clock, fills platform data with aligned-DMA and force-VBUS-active flags, UTMI PHY mode, and reset notification, then creates a `ci_hdrc` child. The reset notification clears all `USBMODE` bits before core mode programming. Remove disables runtime PM, removes the child, and disables the clock.

State and persistence: stores child `ci` platform device, core clock, and platform data. Hardware mode state is reset through the notification path.

Dependencies and integration: integrates with common clock, runtime PM no-callback mode, OF platform matching, and the ChipIdea child-device API.

Risks: `npcm_udc_probe` does not assign `ci->ci = plat_ci` after successful child creation, so remove may dereference an uninitialized child pointer. Device-mode behavior depends on forced VBUS active, which is appropriate for UDC-only designs but not dual-role boards.

Test signals: probe/remove on NPCM hardware, reset notification ordering, aligned DMA transfer tests, and module unload/remove validation to catch the child-pointer issue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_npcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_pci.c

Purpose: provides PCI glue for ChipIdea controllers, turning supported PCI devices into `ci_hdrc` platform children and registering a generic NOP USB PHY.

Important APIs/types/functions: defines `struct ci_hdrc_pci`, static platform data variants for generic, Langwell, and Penwell devices, `ci_hdrc_pci_probe`, `ci_hdrc_pci_remove`, and a PCI ID table for MIPS/Intel devices.

Control flow: probe validates driver data, enables the PCI device with managed PCI helpers, checks IRQ, enables bus mastering/MWI, registers a generic PHY, builds MEM and IRQ resources from BAR0 and PCI IRQ, then calls `ci_hdrc_add_device`. Remove removes the child and unregisters the generic PHY.

State and persistence: stores child `ci` platform device and generic PHY platform device in PCI driver data. PCI resource state is managed by PCI core helpers.

Dependencies and integration: integrates with PCI core, generic USB PHY, ChipIdea platform add/remove, and static platform data describing cap offsets and power budget.

Risks: EHCI PCI driver may bind first unless IDs are bypassed there, as noted in the source. Generic PHY registration must be unwound on child-add failure. Platform data is static and shared, so it must not be mutated in instance-specific ways by consumers.

Test signals: PCI probe/remove, BAR/IRQ resource validation, generic PHY registration, Intel Langwell/Penwell cap-offset behavior, and coexistence with EHCI PCI driver binding rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_tegra.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_tegra.c

Purpose: implements NVIDIA Tegra ChipIdea glue, handling SoC match data, PHY/clock/reset sequencing, runtime PM, Tegra-specific low-power entry, EHCI tuning, and optional double-reset hub behavior.

Important APIs/types/functions: defines `struct tegra_usb`, `struct tegra_usb_soc_info`, match table entries, `tegra_usb_reset_controller`, `tegra_usb_notify_event`, `tegra_usb_internal_port_reset`, `tegra_ehci_hub_control`, `tegra_usb_enter_lpm`, probe/remove, and runtime PM callbacks.

Control flow: probe obtains SoC info, USB PHY, clock, OPP table, runtime-resumes the parent, resets the controller, initializes PHY before touching controller registers, fills platform data, disables runtime PM for ULPI, and adds the `ci_hdrc` child. Hub-control override performs double port reset when requested. Runtime PM gates the parent clock.

State and persistence: stores platform data, child device, SoC info, PHY, clock, and double-reset flag. EHCI tuning is applied on controller reset notifications.

Dependencies and integration: uses Tegra OPP helper, reset controls, USB PHY, OF match data, EHCI internals, runtime PM, and ChipIdea platform add/remove.

Risks: comments note that touching controller AHB-domain registers while clocks are gated can hang the CPU; this is why LPM delegates to `usb_phy_set_suspend`. Port reset override indexes `(wIndex & 0xff) - 1`, so callers must provide valid hub-control requests.

Test signals: Tegra20/30/114/124 probe, runtime suspend/resume, ULPI runtime-PM disable path, double-reset hub requests, EHCI TX fill tuning, and remove power-off sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_usb2.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_usb2.c

Purpose: provides generic OF/platform glue for ChipIdea USB2 controllers, with optional clock management and match-specific platform data for Zynq and Zevio.

Important APIs/types/functions: defines `struct ci_hdrc_usb2_priv`, default/Zynq/Zevio `ci_hdrc_platform_data`, OF match table, `ci_hdrc_usb2_probe`, and `ci_hdrc_usb2_remove`.

Control flow: probe uses existing platform data or allocates default data, overrides it with match data when present, enables an optional clock, sets the platform name, creates the `ci_hdrc` child, stores private state, and enables no-callback runtime PM. Remove disables runtime PM, removes the child, and disables the clock.

State and persistence: private state stores child platform device and clock. Platform data persists in the child device copy created by `ci_hdrc_add_device`.

Dependencies and integration: integrates with OF match data, common clock, runtime PM, PHY/VBUS platform flags, and core ChipIdea child registration.

Risks: match data struct-copy overwrites any preexisting platform data fields, which is intended for compatible-specific defaults but could discard board-provided values if both are supplied. Clock enable failure blocks probe.

Test signals: generic, Zynq, and Zevio compatible probes; optional-clock absence; child probe deferral; and remove/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/core.c

Purpose: implements the ChipIdea core platform driver: register mapping, hardware initialization/reset, PHY/ULPI setup, role initialization and switching, extcon/USB role-switch handling, IRQ dispatch, debugfs setup, runtime/system PM, and exported child-device helpers for glue drivers.

Important APIs/types/functions: exports `ci_hdrc_add_device`, `ci_hdrc_remove_device`, `ci_hdrc_query_available_role`, `hw_read_intr_enable`, `hw_read_intr_status`, `hw_port_test_set/get`, `hw_phymode_configure`, `hw_device_reset`, and `ci_platform_configure`. Main internals are `hw_device_init`, `ci_get_platdata`, `ci_irq_handler`, `ci_get_role`, `ci_hdrc_probe/remove`, and PM helpers.

Control flow: glue drivers call `ci_hdrc_add_device`, which parses platform data and creates a child. Probe maps MMIO, initializes locks/state, ULPI and PHY, detects OTG capability, initializes host/gadget roles according to `dr_mode`, optionally initializes OTG/FSM and role-switch, starts the selected role, requests IRQ, registers extcon notifiers, enables runtime PM, starts FSM, and creates debugfs. IRQ handles low-power wake, OTG/FSM ID/VBUS events, then dispatches active role IRQ.

State and persistence: `struct ci_hdrc` stores persistent role, OTG, endpoint, DMA, PHY, HCD, extcon, quirk, PM, wakeup, and register-map state. Runtime PM uses `in_lpm` and `wakeup_int`; power-loss resume queues revalidation work.

Dependencies and integration: integrates with host/gadget role modules, OTG/FSM, extcon, USB role-switch, PHY and USB PHY frameworks, ULPI, regulators, pinctrl, PM runtime, debugfs, and platform glue.

Risks: role switching spans IRQ-disabled sections, mutexes, runtime PM, and extcon state. Probe has many unwind labels. Power-loss detection reuses `OP_ENDPTLISTADDR`, so false positives/negatives can disrupt resume. `pm_runtime_get_sync` returns are often unchecked.

Test signals: host-only, gadget-only, OTG, extcon, role-switch, FSM, runtime/system suspend/resume, wakeup IRQ, debugfs, and failure-injection of PHY/IRQ/role init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/debug.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/debug.c

Purpose: implements ChipIdea debugfs diagnostics for gadget/device state, port test mode, queue heads, queued requests, OTG FSM variables, and core registers.

Important APIs/types/functions: provides show/write handlers for `device`, `port_test`, `qheads`, `requests`, optional `otg`, and `registers`, plus exported internal hooks `dbg_create_files` and `dbg_remove_files`.

Control flow: `dbg_create_files` creates a debugfs directory named after the device under `usb_debug_root` and installs files. Reads snapshot controller state, often under spinlock and runtime PM. `port_test` write parses a numeric mode and calls `hw_port_test_set`. Remove looks up and removes the directory.

State and persistence: debugfs files do not own state; they expose live `struct ci_hdrc`, gadget driver, endpoint queue-head/TD DMA contents, OTG FSM variables, and MMIO registers. Port-test write mutates hardware test mode.

Dependencies and integration: depends on debugfs, seq_file, runtime PM, gadget/OTG structures, queue-head/TD definitions from UDC code, and register helpers from `ci.h`/`bits.h`.

Risks: qhead/request dumps cast DMA structures to `u32` streams and are only meaningful in gadget mode. `registers` refuses access in low-power mode to avoid unsafe MMIO. Debugfs creation return values are not checked, so missing files are non-fatal.

Test signals: manual debugfs reads in host/gadget/OTG modes, port-test write validation, low-power register read rejection, and queue/request visibility during active gadget transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/host.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/host.c

Purpose: implements the ChipIdea EHCI host role, including HCD creation, VBUS/port-power handling, reset/platform configuration, hub-control quirks, suspend/resume tweaks, and DMA alignment bounce buffering.

Important APIs/types/functions: key functions are `host_start`, `host_stop`, `host_irq`, `ehci_ci_portpower`, `ehci_ci_reset`, `ci_ehci_hub_control`, `ci_ehci_bus_suspend`, DMA alignment helpers, `ci_hdrc_host_init`, `ci_hdrc_host_destroy`, and `ci_hdrc_host_driver_init`.

Control flow: `ci_hdrc_host_driver_init` initializes EHCI overrides. Role init verifies hardware host capability and registers role callbacks. Role start creates an HCD, maps CI registers to EHCI, applies PHY/regulator/pinctrl/platform flags, adds the HCD, and wires OTG host pointer if FSM mode. Hub-control intercepts suspend and clear-suspend cases before delegating to EHCI. Stop removes HCD, synchronizes IRQ, disables early VBUS regulator, clears OTG host, and restores pinctrl.

State and persistence: `ci->hcd` stores the active HCD. EHCI private data stores VBUS regulator and enabled state. Temporary aligned buffers are attached to URBs via `URB_ALIGNED_TEMP_BUFFER`.

Dependencies and integration: depends on EHCI core, regulators, pinctrl, USB PHY VBUS control, ChipIdea platform callbacks, OTG FSM, and host/gadget role state.

Risks: aligned bounce buffers must copy IN data back and always free on map failure/unmap. Host stop sets `ci->role = CI_ROLE_END` directly inside HCD teardown. Multi-port regulator control is explicitly unsupported.

Test signals: EHCI enumeration, VBUS regulator toggling, HSIC suspend/resume notifications, URB alignment stress, hub suspend/resume, role switching, and PM resume with `power_lost`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/host.h -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/host.h

Purpose: declares the ChipIdea host-role initialization, destruction, and EHCI driver setup hooks, with inline no-op or `-ENXIO` stubs when host support is disabled.

Important APIs/types/functions: declares `ci_hdrc_host_init`, `ci_hdrc_host_destroy`, and `ci_hdrc_host_driver_init` under `CONFIG_USB_CHIPIDEA_HOST`; otherwise provides fallback stubs.

Control flow: no runtime flow beyond stubs. The core can call host hooks regardless of Kconfig and receive a clean unsupported-role error.

State and persistence: no owned state; real host implementation populates `ci->roles[CI_ROLE_HOST]` and manages `ci->hcd`.

Dependencies and integration: included by `core.c` and `host.c`, coupling the core role setup to optional EHCI host support.

Risks: host-disabled builds rely on callers handling `-ENXIO`. Empty destroy/init-driver stubs must remain safe when called unconditionally by core init/unwind paths.

Test signals: build and probe host-disabled configurations, host-enabled module init, and error paths where host hardware is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg.c

Purpose: implements ChipIdea OTGSC access abstraction, ID/VBUS role selection, VBUS connect/disconnect handling, ID-based role switching, and OTG workqueue lifecycle.

Important APIs/types/functions: provides `hw_read_otgsc`, `hw_write_otgsc`, `ci_otg_role`, `ci_handle_vbus_change`, `ci_handle_id_switch`, `ci_hdrc_otg_init`, and `ci_hdrc_otg_destroy`; internal worker is `ci_otg_work`.

Control flow: OTGSC reads merge hardware state with extcon or USB role-switch synthetic ID/VBUS state. OTGSC writes clear cable change flags and suppress hardware interrupt enables when external notifiers are used. ID switch locks the role mutex, stops the old role, optionally waits for VBUS to fall before gadget start, starts the new role, and processes VBUS. The workqueue handles ID and B-session-valid events under runtime PM, or delegates to OTG FSM first.

State and persistence: uses `ci->id_event`, `ci->b_sess_valid_event`, `ci->vbus_active`, cable `connected/changed/enabled` fields, current role, workqueue, and OTG FSM state when enabled.

Dependencies and integration: depends on extcon, USB role-switch, gadget VBUS APIs, runtime PM, workqueues, `bits.h` OTGSC masks, and role callbacks from host/gadget modules.

Risks: external connector state deliberately overrides hardware OTGSC bits; incorrect extcon or role-switch updates can force wrong roles. IRQ is disabled while work is queued and must be re-enabled on all paths.

Test signals: ID/VBUS extcon events, role-switch user requests, hardware OTGSC interrupts, VBUS fall wait timeout, gadget VBUS connect/disconnect, and OTG FSM mode delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg.h -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg.h

Purpose: declares ChipIdea OTG helper APIs and provides the shared queued-work helper used by IRQ and FSM paths.

Important APIs/types/functions: prototypes `hw_read_otgsc`, `hw_write_otgsc`, `ci_hdrc_otg_init`, `ci_hdrc_otg_destroy`, `ci_otg_role`, `ci_handle_vbus_change`, and `ci_handle_id_switch`; defines inline `ci_otg_queue_work`.

Control flow: `ci_otg_queue_work` disables the controller IRQ without synchronization, queues `ci->work`, and immediately re-enables the IRQ if the work was already pending.

State and persistence: no state of its own, but the helper operates on `ci->irq`, `ci->wq`, and `ci->work`.

Dependencies and integration: included by core, debug, OTG, and OTG FSM code. It bridges hard IRQ handling to process-context role switching.

Risks: callers must ensure the workqueue has been created before queuing and that IRQ disable/enable balance is preserved if queueing fails due to already-pending work.

Test signals: repeated OTG events while work is pending, destroy/unbind after queued work, and FSM timer callbacks queuing work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg_fsm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg_fsm.c

Purpose: implements ChipIdea support for the Linux USB OTG finite state machine, including HNP/SRP sysfs controls, OTG timers, VBUS driving, local connection/SOF controls, SRP pulsing, role start/stop operations, IRQ event translation, and FSM initialization/removal.

Important APIs/types/functions: public functions are `ci_hdrc_otg_fsm_init`, `ci_hdrc_otg_fsm_start`, `ci_otg_fsm_work`, `ci_otg_fsm_irq`, and `ci_hdrc_otg_fsm_remove`. Key internals include sysfs stores for `a_bus_req`, `a_bus_drop`, `b_bus_req`, `a_clr_err`, timer management, `ci_otg_drv_vbus`, `ci_otg_loc_conn`, `ci_otg_loc_sof`, `ci_otg_start_pulse`, `ci_otg_start_host`, and `ci_otg_start_gadget`.

Control flow: sysfs inputs update FSM fields under `fsm.lock` and queue OTG work. Hrtimer callbacks mark timeout fields and queue work. `ci_otg_fsm_irq` reads OTGSC/intr status, updates FSM variables for ID, BSV, AVV, data pulse, suspend/resume, and port connection events, then queues the state machine. `ci_otg_fsm_work` runs `otg_statemachine` under runtime PM and handles follow-up transitions.

State and persistence: persistent FSM state lives in `ci->fsm`, `ci->otg`, timer arrays, enabled timer bitmask, next timer, gadget HNP flags, runtime PM refs, and regulator/port-power state.

Dependencies and integration: depends on Linux OTG FSM core, gadget and HCD APIs, regulators, runtime PM, ChipIdea role start/stop, OTGSC helpers, and sysfs.

Risks: timer ordering in `ci_otg_del_timer` appears to compare `next_timer` and `cur_timer` in a way that may not select the earliest timeout as intended. Role start/stop in FSM operations assumes both host and gadget roles exist. Runtime PM refs around SRP data pulse must balance.

Test signals: OTG compliance HNP/SRP scenarios, sysfs input toggles, SRP timeout behavior, A/B role swaps, port connect/disconnect IRQs, VBUS regulator transitions, and suspend/resume wake by SRP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg_fsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg_fsm.h -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg_fsm.h

Purpose: defines OTG FSM timing constants for ChipIdea and declares the conditional FSM integration API.

Important APIs/types/functions: constants include `TA_WAIT_VRISE`, `TA_WAIT_VFALL`, `TA_WAIT_BCON`, `TA_AIDL_BDIS`, `TA_BIDL_ADIS`, `TB_DATA_PLS`, `TB_SRP_FAIL`, `TB_ASE0_BRST`, `TB_SE0_SRP`, `TB_SSEND_SRP`, and `TB_AIDL_BDIS`. Declares or stubs `ci_hdrc_otg_fsm_init`, `ci_otg_fsm_work`, `ci_otg_fsm_irq`, `ci_hdrc_otg_fsm_start`, and `ci_hdrc_otg_fsm_remove`.

Control flow: no direct runtime flow except inline stubs when `CONFIG_USB_OTG_FSM` is disabled.

State and persistence: no owned state; constants drive hrtimer scheduling in `otg_fsm.c`.

Dependencies and integration: includes Linux `usb/otg-fsm.h` and is used by core and OTG code to conditionally include FSM behavior.

Risks: timing constants encode USB OTG specification assumptions; changes can affect compliance. Disabled-FSM stubs return success for init but `-ENXIO` for work, so callers must only enter work path when `ci_otg_is_fsm_mode` is true.

Test signals: build with and without `CONFIG_USB_OTG_FSM`, plus OTG SRP/HNP timer compliance tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg_fsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/trace.c

Purpose: instantiates ChipIdea device-mode tracepoints and implements the `ci_log` convenience wrapper.

Important APIs/types/functions: defines `CREATE_TRACE_POINTS`, includes `trace.h`, and implements `ci_log(struct ci_hdrc *ci, const char *fmt, ...)`.

Control flow: `ci_log` builds a `va_format`, calls `trace_ci_log`, and closes the varargs list. Tracepoint generation happens at compile time through `trace.h`.

State and persistence: no persistent state beyond trace buffers populated by enabled trace events. The wrapper snapshots formatted messages at call time.

Dependencies and integration: must be built exactly once when UDC trace support is enabled. Depends on `trace.h` and the kernel tracepoint infrastructure.

Risks: formatted strings are only useful if callers pass a valid `struct ci_hdrc`. Tracepoint code generation is sensitive to include paths, handled by the Makefile.

Test signals: enabling the `chipidea:ci_log` trace event during gadget transfers and building UDC trace support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/chipidea/trace.h

Purpose: defines ChipIdea gadget-mode tracepoints for formatted controller logs and transfer descriptor preparation/completion.

Important APIs/types/functions: declares `TRACE_SYSTEM chipidea`, `CHIPIDEA_MSG_MAX`, `ci_log`, `TRACE_EVENT(ci_log)`, event class `ci_log_trb`, and concrete events `ci_prepare_td` and `ci_complete_td`.

Control flow: no direct runtime flow; tracepoint macros generate logging hooks. `ci_log_trb` snapshots endpoint name, request pointer, TD pointer/DMA, remaining size, next pointer, token, and endpoint type, then formats transfer size/status fields.

State and persistence: trace events persist in ftrace buffers only. They expose live request/TD metadata but do not mutate controller state.

Dependencies and integration: includes ChipIdea core and UDC headers because it references `struct ci_hw_ep`, `struct ci_hw_req`, `struct td_node`, TD token masks, and endpoint descriptors. The trailing `define_trace.h` block requires Makefile include-path support.

Risks: trace callers must pass valid endpoint/request/TD pointers. TD token decoding depends on UDC data-structure layout and masks staying consistent.

Test signals: build with `CONFIG_USB_CHIPIDEA_UDC`, enable `chipidea:ci_prepare_td` and `chipidea:ci_complete_td`, then run gadget transfer tests to verify TD lifecycle traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/chipidea/trace.h -->
