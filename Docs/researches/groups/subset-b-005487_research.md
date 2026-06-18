# subset-b-005487 research

Grouped research for the DWC3 glue-layer and endpoint-zero files in `sources/distributed-fs/ceph-client/drivers/usb/dwc3`. Each section is bounded for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-imx8mp.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-imx8mp.c

Purpose: NXP i.MX8MP USB3 glue driver that owns the HSIO wakeup block, optional USB glue registers, wrapper clocks, wake IRQ, and the child `snps,dwc3` core. It adds software-node xHCI quirks and installs a DWC3 glue callback to adjust runtime autosuspend before role changes.

Important APIs, types, and functions: `struct dwc3_imx8mp` persists the parent device, child DWC3 platform device, HSIO/glue MMIO bases, `hsio` and `suspend` clocks, IRQ, and suspend/wakeup flags. `imx8mp_configure_glue()` programs permanent-attach, port-power-control, over-current polarity, and power polarity properties. `dwc3_imx8mp_wakeup_enable()` and `_disable()` manage `USB_WAKEUP_CTRL`. `dwc3_imx8mp_interrupt()` handles wake events while suspended. `dwc3_imx_pre_set_role()` is exported through `dwc3_imx_glue_ops`.

Control flow: probe maps resource 0 as HSIO, optionally maps resource 1 as glue, enables both clocks, finds the `snps,dwc3` child, applies glue configuration, enables runtime PM, attaches the software node, populates the child core, retrieves the child platform data, sets `dwc3->glue_ops`, requests the wake IRQ, and marks the parent wake-capable. Remove puts the child device, depopulates children, removes the software node, and disables runtime PM. System and runtime suspend share `dwc3_imx8mp_suspend()`; resume restores wake bits, glue registers, clocks, runtime-PM state, and any disabled IRQ.

State and persistence: persistent state is MMIO configuration plus `pm_suspended` and `wakeup_pending`. The driver intentionally re-runs `imx8mp_configure_glue()` after resume because power loss can clear wrapper registers. Wake handling depends on the child `struct dwc3` role and `xhci` pointer.

Dependencies and integration: uses OF child population, platform resources, Linux clocks, runtime/system PM, wake IRQs, `device_add_software_node()`, and DWC3 internals from `core.h`. It integrates with xHCI in host mode by resuming the xHCI child from the wrapper IRQ, and with gadget mode by runtime-getting the DWC3 device.

Risks: `dwc3_imx8mp_interrupt()` assumes a valid child DWC3 pointer when suspended. Missing glue resource is tolerated but disables board-specific polarity and permanent-attach behavior. Clock sequencing and wake IRQ enable/disable paths are sensitive to system suspend versus autosuspend differences. Role-change autosuspend policy can break wake behavior if `dwc3->current_dr_role` lags the requested role.

Test signals: probe should create a child DWC3 core, expose xHCI quirks, and log missing optional glue resource only as a warning. Suspend/resume tests should cover host wake from DPDM/U3/SS connect, device wake from VBUS/session, i.MX95 out-of-band wake setup, runtime autosuspend, and role switches between host and device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-imx8mp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-keystone.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-keystone.c

Purpose: TI Keystone and AM654 DWC3 wrapper driver. It powers the optional USB3 PHY, enables wrapper IRQ forwarding where required, and populates the child `snps,dwc3` core.

Important APIs, types, and functions: `struct dwc3_keystone` stores the parent device, USBSS MMIO base, and optional `usb3_phy`. `kdwc3_readl()` and `kdwc3_writel()` wrap register access. `kdwc3_enable_irqs()` and `_disable_irqs()` program `USBSS_IRQENABLE_SET_0`. `dwc3_keystone_interrupt()` clears, re-enables, and EOIs core IRQ status. `kdwc3_probe()` and `kdwc3_remove()` own resource lifecycle.

Control flow: probe allocates private data, maps USBSS registers, gets the optional `usb3-phy`, runtime-resumes the PHY, resets/initializes/powers it, enables runtime PM on the wrapper, optionally skips IRQ setup for `ti,am654-dwc3`, requests the shared IRQ for older Keystone, enables wrapper IRQs, and populates children. Removal disables IRQs for non-AM654, unregisters children, drops runtime PM, powers off/exits the PHY, and releases PHY runtime PM.

State and persistence: no software state beyond private pointers is durable. Hardware state consists of the PHY power/init state and wrapper IRQ enable/status registers. The interrupt handler always acknowledges and re-arms the wrapper interrupt rather than inspecting child DWC3 event content.

Dependencies and integration: depends on platform MMIO, OF population, the generic PHY framework, and runtime PM. It integrates with the DWC3 core by creating the OF child device and with TI wrapper interrupt routing through USBSS registers.

Risks: error paths after `phy_pm_runtime_get_sync()` must unwind PHY power/init state correctly. AM654 skips IRQ processing entirely, so compatible matching must reflect hardware behavior. The IRQ handler writes enable/status/EOI registers unconditionally, so incorrect resource mapping or sharing could mask interrupts.

Test signals: boot logs should show successful PHY reset/init/power-on and child creation. Regression tests should exercise non-AM654 interrupt handling, AM654 no-IRQ probe path, PHY probe defer, and removal/unbind cleanup without dangling child devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-keystone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-meson-g12a.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-meson-g12a.c

Purpose: Amlogic Meson USB control/glue driver for GXL, GXM, AXG, G12A, and A1 families. It configures USB2 per-port controls, USB3 glue registers, PHY modes, clocks, resets, optional VBUS regulator, OTG ID interrupt handling, and a userspace-visible role switch spanning DWC3 and DWC2 children.

Important APIs, types, and functions: `struct dwc3_meson_g12a_drvdata` selects clocks, PHY names, register-map setup, USB2 init, PHY mode operations, and post-init hooks per SoC. `struct dwc3_meson_g12a` stores regmaps, reset, PHYs, mode/role state, regulator, role-switch descriptors, and port counts. Core functions include `dwc3_meson_g12a_usb2_init_phy()`, `dwc3_meson_g12a_usb3_init()`, `dwc3_meson_g12a_usb_otg_apply_mode()`, `dwc3_meson_g12a_otg_mode_set()`, `dwc3_meson_g12a_irq_thread()`, `dwc3_meson_g12a_setup_regmaps()`, and `dwc3_meson_g12a_probe()`.

Control flow: probe maps the wrapper MMIO, selects drvdata from OF match data, gets optional VBUS, enables SoC clocks, resets the block, discovers optional PHYs and port counts, creates regmaps, enables VBUS, initializes wrapper registers for the initial `dr_mode`, initializes and powers PHYs, runs post-init for GXL-style hardware, populates children, registers OTG IRQ and role switch, then enables runtime PM. OTG IRQ reads `USB_R5` ID state and calls `dwc3_meson_g12a_otg_mode_set()` when the pin changes. Role-switch set maps USB host/device roles to PHY host/device modes and optional VBUS changes.

State and persistence: persisted state includes current `otg_mode`, `otg_phy_mode`, discovered `usb2_ports` and `usb3_ports`, role-switch handles, and hardware register programming. System suspend powers off/exits PHYs, disables host VBUS, and rearms reset; resume resets the block, reruns USB init, reinitializes/powers PHYs, restores VBUS, and reruns post-init.

Dependencies and integration: uses regmap over MMIO, reset controls, clk bulk APIs, generic PHY, regulator, OF child population, `usb_role_switch`, USB OTG helpers, and runtime/system PM. It links DWC3 and DWC2 children into a single role-switch descriptor with `usb2_port` and `udc` device references.

Risks: the GXL/GXM workaround for broken device-to-host switching uses host-port disable and a 500 ms sleep; manual OTG switching can still be fragile. The `gxl_drvdata` and `gxm_drvdata` clock/PHY table choices are easy to regress because they intentionally differ from G12A. Optional PHY arrays have fixed `PHY_COUNT`, so DT binding mismatches can silently change port counts. VBUS regulator changes must stay consistent with role state to avoid back-powering.

Test signals: test each compatible string, USB2-only A1/AXG cases, SuperSpeed initialization when a USB3 PHY exists, role switching from ID IRQ and userspace, VBUS regulator enable/disable, suspend/resume restoration, and child device reference cleanup during remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-meson-g12a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-octeon.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-octeon.c

Purpose: Cavium/Marvell Octeon III DWC3 UCTL wrapper driver. It parses board clock and power-control properties, programs 64-bit UCTL registers, sets endian mode, releases PHY reset, and populates the child DWC3 core in host mode.

Important APIs, types, and functions: `struct dwc3_octeon` stores the parent device and UCTL MMIO base. `dwc3_octeon_readq()` and `_writeq()` use Octeon CSR accessors when available. `dwc3_octeon_config_gpio()` wires Octeon GPIO outputs for port power. `dwc3_octeon_get_divider()` selects a controller clock divider from IO clock rate. `dwc3_octeon_setup()` implements the hardware init sequence. `dwc3_octeon_set_endian_mode()`, `_phy_reset()`, and `_probe()` finish setup.

Control flow: probe requires `refclk-frequency`, `refclk-type-ss`, and `refclk-type-hs`, converts those to reference-clock selector, fsel, and MPLL multiplier values, reads optional `power` GPIO tuple, maps UCTL registers, runs the ordered setup sequence, sets DMA/CSR endian bits, deasserts PHY reset, stores private data, and populates the OF child. Removal only depopulates children.

State and persistence: state is primarily hardware state in `USBDRD_UCTL_CTL`, `HOST_CFG`, and `SHIM_CFG`. The setup sequence asserts resets, sets dividers and reference clocks, powers HS/SS PHYs, deasserts UCTL and UAHC resets, enables clocks, configures port power polarity, and forces host mode. There is no PM restore path, so firmware or full reprobe is expected after reset-level loss.

Dependencies and integration: depends on Octeon SOC CSR helpers under `CONFIG_CAVIUM_OCTEON_SOC`, OF properties, MMIO, delays, and OF child population. It integrates with board GPIO routing for power control and with the DWC3 child through the standard `snps,dwc3` node.

Risks: invalid clock properties fall back or fail depending on field, so board DT accuracy is critical. The non-Octeon stubs return zero reads and no-op writes, making the driver only meaningful on Octeon builds. There is no runtime/system PM handling; suspend behavior depends on wider platform handling. Power GPIO tuple parsing is nonstandard and easy to mis-specify.

Test signals: verify UCTL clock divider selection across IO clock rates, refclk combinations at 50/100/125 MHz, host-only operation, endian correctness on big-endian kernels, GPIO power polarity, and child DWC3 probe after UCTL reset release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-of-simple.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-of-simple.c

Purpose: generic OF glue driver for simple DWC3 integrations that need only reset deassertion, bulk clock enablement, OF child population, and minimal PM handling. It covers Rockchip RK3399, Spreadtrum, Allwinner, HiSilicon, and Intel Keem Bay compatibles.

Important APIs, types, and functions: `struct dwc3_of_simple` stores device, bulk clock array, clock count, reset array, and a `need_reset` flag. `dwc3_of_simple_probe()` owns setup. `__dwc3_of_simple_teardown()` centralizes remove and shutdown cleanup. Runtime PM callbacks disable/enable clocks, while system sleep callbacks optionally assert/deassert resets for RK3399.

Control flow: probe allocates private state, marks RK3399 as needing reset toggles during system sleep, gets optional exclusive reset array, deasserts resets, gets all clocks, enables them, populates the DWC3 child, and enables runtime PM. Remove and shutdown depopulate children, disable and put clocks, assert and put resets, disable runtime PM, and mark the device suspended.

State and persistence: software state is limited to the reset and clock handles plus `need_reset`. Hardware state consists of reset deassertion and clocks being active. Runtime suspend gates clocks without unpreparing; runtime resume re-enables them. System sleep reset handling is conditional and does not restore additional registers.

Dependencies and integration: depends on OF, platform child population, reset controller arrays, bulk clock APIs, and runtime PM. It deliberately avoids SoC-specific register programming.

Risks: it is only appropriate for wrappers with no hidden register sequencing. The teardown helper is shared by remove and shutdown, so repeated or late calls must not race with child devices. `pm_runtime_get_sync()` result is not checked in probe, so unusual PM failures could go unnoticed.

Test signals: compatible-specific smoke tests should verify reset deassert, all-clock enablement, child DWC3 creation, runtime clock gating, RK3399 sleep reset toggling, shutdown cleanup, and probe deferral on clocks/resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-of-simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-omap.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-omap.c

Purpose: TI OMAP/AM437x DWC3 wrapper driver. It programs wrapper register offsets, UTMI OTG software/hardware mode, extcon-driven VBUS/ID mailbox signals, wrapper IRQ masking/acknowledgement, optional VBUS regulator, and child DWC3 population.

Important APIs, types, and functions: `struct dwc3_omap` stores IRQ, MMIO base, variant offsets, saved UTMI control value, extcon notifiers, and VBUS regulator. `dwc3_omap_set_mailbox()` maps extcon status into UTMI control bits and regulator state. `dwc3_omap_interrupt()` and `_interrupt_thread()` implement masked threaded IRQ handling. `dwc3_omap_map_offset()` handles AM437x offset deltas. `dwc3_omap_set_utmi_mode()` applies DT `utmi-mode`. Probe/remove and sleep callbacks manage lifecycle.

Control flow: probe validates DT, gets IRQ and MMIO, optionally gets `vbus`, enables runtime PM, maps offsets, sets UTMI mode, registers extcon notifiers and seeds initial mailbox state, populates the child DWC3 core, requests a shared threaded IRQ, and enables wrapper IRQ bits. IRQ top half masks interrupts and wakes the thread when misc/core status is present; the thread clears status and re-enables IRQs. Suspend saves UTMI control and disables IRQs; resume restores UTMI and IRQs; complete resynchronizes extcon mailbox state.

State and persistence: persistent software state includes wrapper offset fields, saved `utmi_otg_ctrl`, extcon handles, and regulator pointer. Hardware state lives in UTMI OTG control and IRQ enable/status registers. Extcon notifications update VBUS valid/session/end and IDDIG bits.

Dependencies and integration: uses extcon for cable and host ID state, regulator framework for VBUS sourcing in host mode, platform MMIO/IRQ, OF child population, and runtime/system PM. It integrates with child DWC3 through the standard child node and with wrapper event routing through IRQ0 and IRQMISC registers.

Risks: `dwc3_omap_complete()` assumes `omap->edev` is valid, so sleep paths without extcon need scrutiny. Offset arithmetic differs for AM437x, creating risk of writing wrong registers if compatible is wrong. Regulator enable/disable is driven by ID status and must not conflict with external power. IRQ clear/mask order is central to avoiding storms or lost events.

Test signals: test extcon VBUS/ID transitions, regulator behavior on host attach/detach, AM437x and generic offset paths, IRQ masking/clearing under shared IRQ, suspend/resume restore, and child depopulation on probe failure and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-omap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-pci.c

Purpose: PCI glue driver that turns Intel and AMD PCI DWC3 controllers into a child `dwc3` platform device with synthesized resources and software-node properties. It handles Intel/AMD quirks, Bay Trail GPIO/refclock setup, ACPI DSM power transitions, and runtime wake work.

Important APIs, types, and functions: `struct dwc3_pci` stores the child platform device, PCI device, DSM GUID, PM flag, and resume work. Software nodes provide properties such as `dr_mode`, `linux,sysdev_is_parent`, PHY charger detection, reserved endpoints, AMD link quirks, and role-switch defaults. `dwc3_byt_enable_ulpi_refclock()` clears Bay Trail ULPI refclock disable. `dwc3_pci_quirks()` applies vendor/device-specific setup. `dwc3_pci_probe()`, `_remove()`, `_dsm()`, and PM callbacks own lifecycle.

Control flow: probe enables the PCI function, sets bus mastering, allocates a `dwc3` platform device, maps BAR0 and PCI IRQ into platform resources, sets parent and ACPI companion, applies quirk software node and platform-specific GPIO/refclock handling, registers the child, enables wakeup, stores driver data, and initializes resume work. Runtime/system suspend invoke DSM D3 for selected Intel devices; resume invokes DSM D0 and queues work that runtime-resumes the child DWC3 device.

State and persistence: software node properties persist on the child until removal. `has_dsm_for_pm` and `guid` persist per PCI function. Bay Trail fallback GPIO lookup table may be globally added and is removed on device removal. Runtime PM state is split between the PCI parent and child platform device.

Dependencies and integration: depends on PCI, ACPI, DMI, GPIO lookup/descriptor APIs, workqueues, platform-device creation, and PM. It integrates with DWC3 core entirely through the child platform device and property injection rather than OF.

Risks: many device IDs share the same software node, so adding IDs can accidentally select wrong mode/quirks. Bay Trail GPIO fallbacks are board-sensitive and use global lookup table mutation. Runtime resume queues child PM work asynchronously, which can hide ordering bugs. DSM failures block PM transitions on affected Intel devices.

Test signals: enumerate supported Intel and AMD PCI IDs, verify child resources match BAR0/IRQ, confirm software-node properties in sysfs or debug, exercise Bay Trail refclock/GPIO paths, check AMD quirk application, and test runtime/system suspend with and without DSM-capable devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-qcom-legacy.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-qcom-legacy.c

Purpose: legacy Qualcomm DWC3 glue driver for `qcom,dwc3` devices. It controls QSCRATCH VBUS override, resets, manually acquired clocks, optional extcon role notifications, interconnect bandwidth, wakeup PHY IRQs, and an OF-populated child `snps,dwc3` platform device.

Important APIs, types, and functions: `struct dwc3_qcom` stores parent device, QSCRATCH base, child `platform_device *dwc3`, clock array, resets, per-port wake IRQs, extcon devices/notifiers, PM flags, and interconnect paths. `dwc3_qcom_register_extcon()` wires VBUS and host extcon notifications. `dwc3_qcom_suspend()` and `_resume()` gate clocks/interconnects and enable/disable wake IRQs. `dwc3_qcom_of_register_core()` populates and locates the child core. `dwc3_qcom_clk_init()` manually obtains and enables clocks.

Control flow: probe asserts/deasserts resets, gets/enables clocks, maps QSCRATCH, sets up per-port IRQs, optionally selects UTMI as PIPE clock, populates the child DWC3 core, initializes interconnect bandwidth, reads child `dr_mode`, enables VBUS override unless host-only, registers extcon notifiers, initializes wakeup on parent and child, and enables then forbids runtime PM. Extcon callbacks toggle VBUS override and update `mode`. Suspend checks HS PHY L2 status, disables clocks and interconnects, then enables wake IRQs if host and wakeup is allowed; resume reverses that and clears L2 event bits.

State and persistence: state is split between parent QSCRATCH registers, child DWC3 device state, extcon role state, per-port cached USB2 speeds, and interconnect bandwidth handles. `is_suspended` prevents duplicate suspend. `pm_suspended` lets wake IRQs defer work to system resume.

Dependencies and integration: uses OF child population, extcon, reset controller, legacy clock APIs, interconnect framework, USB HCD root-hub inspection, platform IRQ names, and runtime/system PM. It integrates with DWC3 via child platform data and with host wake via PHY IRQs named `dp_hs_phy`, `dm_hs_phy`, `ss_phy`, and optional multiport variants.

Risks: this file intentionally differs from modern `dwc3-qcom.c`; mixing assumptions between them can break child lifecycle or PM. Host detection peeks into child `struct dwc3` and xHCI state, a layering violation with race potential during probe/remove. Extcon state drives VBUS override and mode but may conflict with role-switch based systems. Manual clock unwind must stay exact.

Test signals: test legacy `qcom,dwc3` DTs with and without extcon, one-port and multiport IRQ naming, runtime/system wake from suspended host, interconnect enable/disable errors, VBUS override in peripheral and host modes, and child depopulation/put on probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-qcom-legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-qcom.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-qcom.c

Purpose: modern Qualcomm DWC3 glue driver for `qcom,snps-dwc3`. It embeds `struct dwc3` in the glue object and invokes `dwc3_core_probe()` directly, while managing QSCRATCH VBUS override, clocks, resets, interconnects, wakeup IRQs, PM, and DWC3 glue callbacks for role and run/stop transitions.

Important APIs, types, and functions: `struct dwc3_qcom` embeds `struct dwc3 dwc`, stores QSCRATCH base, bulk clocks, resets, per-port IRQs/speeds, mode/current role, PM flags, and interconnect paths. `to_dwc3_qcom()` converts embedded core to glue. `dwc3_qcom_vbus_override_enable()`, interconnect helpers, IRQ setup helpers, `dwc3_qcom_suspend()` and `_resume()`, `dwc3_qcom_set_role_notifier()`, and `dwc3_qcom_run_stop_notifier()` are central. `dwc3_qcom_glue_ops` feeds callbacks to the DWC3 core.

Control flow: probe gets resets and all clocks, toggles resets, enables clocks, carves the DWC3 core resource before the SDM845 QSCRATCH offset, maps QSCRATCH, sets up named wake IRQs, optionally selects UTMI as PIPE clock, determines initial role and VBUS override policy, sets `dwc.glue_ops`, fills `dwc3_probe_data` with default properties and `ignore_clocks_and_resets`, calls `dwc3_core_probe()`, initializes interconnects, and configures wakeup. PM suspend first calls DWC3 core PM then wrapper suspend; resume restores wrapper then DWC3 core.

State and persistence: embedded DWC3 state persists in the same allocation as glue state. `current_role` tracks role-switch transitions and drives QSCRATCH VBUS override. `is_suspended` prevents duplicate wrapper suspend. Per-port `usb2_speed` is cached before enabling wake IRQs so DP/DM edge polarity can match attached device speed.

Dependencies and integration: depends on DWC3 internal `core.h` and `glue.h`, reset/clock/interconnect frameworks, USB role and HCD helpers, platform IRQ naming, runtime/system PM, and QSCRATCH MMIO. Direct `dwc3_core_probe()` integration avoids a child platform device and lets glue callbacks run inside core role/run-stop paths.

Risks: host detection and speed reading still inspect xHCI/root-hub state, so timing around role changes and suspend matters. Resource splitting assumes SDM845-style QSCRATCH offset/size. Wake IRQ polarity is speed-dependent and can misfire if cached speed is stale. VBUS override callback logic is subtle: leaving device role disables override, entering non-device paths can enable it.

Test signals: validate direct core probe/remove, role-switch transitions, gadget run/stop VBUS override, UTMI-as-PIPE operation, one-port and four-port wake IRQ setups, host suspend with LS/FS/HS/no device attached, interconnect bandwidth programming by maximum speed, and system/runtime PM ordering with DWC3 core PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-qcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-rtk.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-rtk.c

Purpose: Realtek DWC3 glue driver for `realtek,rtd-dwc3`. It programs wrapper workarounds, USB2/USB3 PHY routing, optional PM control registers, child DWC3 creation, and a wrapper-level USB role switch that synchronizes the DWC3 role and Realtek USB2 PHY switch bits.

Important APIs, types, and functions: `struct dwc3_rtk` stores device, wrapper MMIO, optional PM MMIO, child `struct dwc3 *`, current role, and optional role switch. `dwc3_rtk_init()` applies SOC-specific workarounds and PHY/DBUS setup. `switch_usb2_role()`, `switch_dwc3_role()`, `dwc3_rtk_set_role()`, and role-switch callbacks manage role transitions. `__get_dwc3_maximum_speed()` reads child maximum speed. `dwc3_rtk_probe_dwc3_core()` populates and locates the child core.

Control flow: probe maps wrapper and optional PM resources, then calls `dwc3_rtk_probe_dwc3_core()`. Core probing first runs wrapper init, populates the OF child, finds the `snps,dwc3` platform device and drvdata, reconciles DT `dr_mode` with core `dr_mode`, sets the initial role, optionally registers a userspace-controllable role switch, and programs USB2 role bits. Remove clears the child pointer, unregisters role switch, and depopulates children. Resume reruns wrapper init and reapplies the last role.

State and persistence: `cur_role` is the persistent software role and is re-applied after resume. Hardware state includes workaround bits for multi-request/DESC behavior, USB2 PLL and role-switch bits, USB3 disable/power-bias bits for high-speed-only configurations, and optional DBUS power-control enable.

Dependencies and integration: uses OF child population, `soc_device_match()` for Realtek family/revision workarounds, USB role-switch framework, DWC3 internals from `core.h`, PM sleep callbacks, and optional Realtek USB2/USB3 PHY softdeps.

Risks: the role switch calls into the child DWC3 role switch and then delays before changing wrapper USB2 bits; ordering is hardware-sensitive. SOC workaround matches are string-based and can miss new revisions. `rtk->dwc` is cleared before role-switch unregister, so callbacks must not race removal. High-speed-only paths disable USB3 PHY resources based on child `maximum-speed`, making DT correctness critical.

Test signals: verify each Realtek SOC workaround, high-speed-only PHY disablement, initial host/device role programming, userspace role switching, child probe failure unwind, resume reinitialization, and no role-switch callbacks after remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-rtk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-st.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-st.c

Purpose: STMicroelectronics STi DWC3 glue driver. It manages glue registers, syscfg regmap configuration for static host/device mode, powerdown and soft reset controls, child DWC3 population, and sleep-state pinctrl/reset handling.

Important APIs, types, and functions: `struct st_dwc3` stores device, glue MMIO, syscfg regmap, syscfg register offset, `dr_mode`, and reset controls. `st_dwc3_drd_init()` programs static DRD mode into syscfg bits. `st_dwc3_init()` configures clock/reset glue, xHCI revision selection, and VBUS/powerpresent/bvalid muxing. `st_dwc3_probe()`, `_remove()`, `_suspend()`, and `_resume()` own lifecycle.

Control flow: probe maps named `reg-glue`, gets `st,syscfg` regmap and `syscfg-reg` offset, finds the child DWC3 node, deasserts powerdown and softreset controls, populates the child, finds the child platform device to read `dr_mode`, programs static host/device syscfg through `st_dwc3_drd_init()`, initializes glue registers, and stores private data. Suspend asserts resets and selects sleep pinctrl; resume restores default pinctrl, deasserts resets, reruns DRD syscfg, and reruns glue init.

State and persistence: persistent state is static `dr_mode`, reset handles, and register offsets. Hardware state in syscfg and glue registers is restored on resume. OTG/dual-role dynamic switching is not implemented; only host or peripheral static modes are accepted.

Dependencies and integration: depends on MFD syscon/regmap, reset framework, pinctrl PM helpers, OF child population, USB dr_mode helpers, and DWC3 child platform device discovery. It includes DWC3 `core.h`/`io.h` but mainly interacts through child creation.

Risks: unsupported `dr_mode` returns `-EINVAL`, so DT must not request OTG. Bit masking in `st_dwc3_drd_init()` relies on syscfg layout matching `st,stih407-dwc3`. Probe configures DRD after child population, so child behavior during early probe must tolerate wrapper defaults. Reset ordering during suspend/resume is hardware-sensitive.

Test signals: test host and peripheral DT modes, unsupported OTG rejection, syscfg write failures, child discovery failure paths, reset assert/deassert sequencing, glue register values after resume, and pinctrl sleep/default transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-xilinx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-xilinx.c

Purpose: Xilinx ZynqMP and Versal DWC3 glue driver. It manages clocks, platform-specific resets, optional USB3 PHY, ULPI reset masking, coherent DMA traffic routing, software-node property injection for coherent children, OF child creation, and PM clock/PHY handling.

Important APIs, types, and functions: `struct dwc3_xlnx` stores bulk clocks, device, wrapper MMIO, platform init callback, and optional USB3 PHY. `dwc3_xlnx_mask_phy_rst()` controls whether the USB controller may reset ULPI PHY. `dwc3_xlnx_set_coherency()` routes DMA through FPD when coherent or IOMMU-mapped. `dwc3_xlnx_init_versal()` and `_init_zynqmp()` implement SoC-specific reset/PHY flows. `dwc3_set_swnode()` injects `snps,gsbuscfg0-reqinfo` when the child DWC3 node is coherent.

Control flow: probe maps registers, selects init callback from OF match data, enables all clocks, runs Versal or ZynqMP init, optionally creates a managed software node, populates child devices, sets runtime PM active, enables devm runtime PM, and runtime-resumes the wrapper. ZynqMP init optionally initializes/powers USB3 PHY, deasserts APB/core/hibernation resets, selects or deselects PIPE clock, handles optional reset GPIO, and sets coherency. Versal masks/unmasks PHY reset around reset assertion/deassertion and configures USB2 traffic route coherency.

State and persistence: platform init writes wrapper reset, PIPE clock, power-present, traffic-route, and PHY reset mask registers. System suspend exits the USB3 PHY and disables clocks; resume enables clocks and reinitializes/powers the PHY. Runtime suspend/resume gates clocks only.

Dependencies and integration: uses OF match data, bulk clocks, reset controls, optional GPIO reset, generic PHY, PM runtime, OF child population, DMA coherency/IOMMU helpers, and managed software nodes. It integrates with child DWC3 by child node population and property injection.

Risks: ZynqMP reset behavior changes depending on whether `usb3-phy` exists; missing DT PHY can avoid resets even when USB3 is actually used. `dwc3_set_swnode()` attaches the software node to the wrapper device, so property inheritance expectations must match DWC3 core behavior. PM paths do not rerun full platform init, only clocks/PHY, so register retention matters. Coherency routing must match DMA/IOMMU configuration.

Test signals: test both compatibles, USB3 PHY present and absent, reset GPIO sequencing, coherent/IOMMU traffic route bits, software-node property creation for coherent child nodes, runtime clock gating, system suspend/resume with PHY reinit, and probe failure unwind after child population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-xilinx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/ep0.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/ep0.c

Purpose: DWC3 gadget endpoint-zero control-transfer engine. It manages setup, data, and status phases for USB control requests on physical EP0/EP1, queues TRBs, delegates class/vendor requests to gadget drivers, handles standard Chapter 9 requests, stalls/restarts on protocol errors, and consumes DWC3 endpoint events.

Important APIs, types, and functions: external entry points include `dwc3_gadget_ep0_queue()`, `dwc3_gadget_ep0_set_halt()`, `dwc3_ep0_out_start()`, `dwc3_ep0_stall_and_restart()`, `dwc3_ep0_send_delayed_status()`, `dwc3_ep0_end_control_data()`, and `dwc3_ep0_interrupt()`. Internal helpers include `dwc3_ep0_prepare_one_trb()`, `dwc3_ep0_start_trans()`, `__dwc3_gadget_ep0_queue()`, `dwc3_ep0_std_request()`, `dwc3_ep0_inspect_setup()`, `dwc3_ep0_complete_data()`, `dwc3_ep0_complete_status()`, and `dwc3_ep0_xfernotready()`.

Control flow: `dwc3_ep0_out_start()` arms an 8-byte CONTROL_SETUP TRB on EP0 OUT. When `dwc3_ep0_interrupt()` sees XFERCOMPLETE in setup state, `dwc3_ep0_inspect_setup()` parses the setup packet from `ep0_trb`, determines two-stage versus three-stage transfer, handles standard requests locally or delegates to the gadget driver, and stalls on errors. For three-stage requests, `__dwc3_gadget_ep0_queue()` starts the data TRB as soon as the gadget driver queues the request. XferNotReady STATUS moves to status phase and starts CONTROL_STATUS2/3 unless delayed status is active. Completion handlers give back queued requests, handle test mode, restart setup, or mark setup-pending.

State and persistence: key state lives in `struct dwc3`: `ep0state`, `ep0_next_event`, `three_stage_setup`, `ep0_expect_in`, `delayed_status`, `setup_packet_pending`, `ep0_bounced`, `test_mode`, U1/U2/SEL timing fields, and gadget state. EP flags such as `DWC3_EP_PENDING_REQUEST`, `DWC3_EP0_DIR_IN`, `DWC3_EP_TRANSFER_STARTED`, `DWC3_EP_END_TRANSFER_PENDING`, `DWC3_EP_STALL`, and `DWC3_EP_WEDGE` drive queueing and halt behavior. TRB enqueue indexes for EP0/EP1 are reset after stalls and bounce completions.

Dependencies and integration: depends on DWC3 core/gadget/io helpers, USB gadget/composite APIs, Chapter 9 constants, spinlock protection, DMA mapping, request giveback, DWC3 DEPCMD/DEPEVT event semantics, and tracepoints. It integrates with gadget drivers through `gadget_driver->setup()`, delayed-status return values, and `usb_ep_queue()` callbacks.

Risks: EP0 and EP1 share one TRB ring, so pending-list and `trb_enqueue` rules are strict. OUT transfers that are not maxpacket-aligned need bounce TRBs because the controller cannot handle them directly. Back-to-back setup packets and SETUP_PENDING TRB status require status-phase completion before returning to setup. Lock dropping in `dwc3_ep0_delegate_req()` when async callbacks are enabled can expose races if state assumptions change. Incorrect delayed-status handling can leave enumeration stuck.

Test signals: run USB gadget enumeration, Chapter 9 GET_STATUS/SET_ADDRESS/SET_CONFIGURATION/SET/CLEAR_FEATURE, U1/U2 enable/disable, Set SEL, Set Isoch Delay, endpoint halt/wedge clear, delayed-status composite functions, control OUT unaligned transfers, zero-length packets, back-to-back setup packets, test mode requests, disconnect during pending request, and XferNotReady wrong-direction stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/ep0.c -->
