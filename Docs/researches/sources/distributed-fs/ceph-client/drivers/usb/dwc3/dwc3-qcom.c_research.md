# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-qcom.c

Purpose: modern Qualcomm DWC3 glue driver for `qcom,snps-dwc3`. It embeds `struct dwc3` in the glue object and invokes `dwc3_core_probe()` directly, while managing QSCRATCH VBUS override, clocks, resets, interconnects, wakeup IRQs, PM, and DWC3 glue callbacks for role and run/stop transitions.

Important APIs, types, and functions: `struct dwc3_qcom` embeds `struct dwc3 dwc`, stores QSCRATCH base, bulk clocks, resets, per-port IRQs/speeds, mode/current role, PM flags, and interconnect paths. `to_dwc3_qcom()` converts embedded core to glue. `dwc3_qcom_vbus_override_enable()`, interconnect helpers, IRQ setup helpers, `dwc3_qcom_suspend()` and `_resume()`, `dwc3_qcom_set_role_notifier()`, and `dwc3_qcom_run_stop_notifier()` are central. `dwc3_qcom_glue_ops` feeds callbacks to the DWC3 core.

Control flow: probe gets resets and all clocks, toggles resets, enables clocks, carves the DWC3 core resource before the SDM845 QSCRATCH offset, maps QSCRATCH, sets up named wake IRQs, optionally selects UTMI as PIPE clock, determines initial role and VBUS override policy, sets `dwc.glue_ops`, fills `dwc3_probe_data` with default properties and `ignore_clocks_and_resets`, calls `dwc3_core_probe()`, initializes interconnects, and configures wakeup. PM suspend first calls DWC3 core PM then wrapper suspend; resume restores wrapper then DWC3 core.

State and persistence: embedded DWC3 state persists in the same allocation as glue state. `current_role` tracks role-switch transitions and drives QSCRATCH VBUS override. `is_suspended` prevents duplicate wrapper suspend. Per-port `usb2_speed` is cached before enabling wake IRQs so DP/DM edge polarity can match attached device speed.

Dependencies and integration: depends on DWC3 internal `core.h` and `glue.h`, reset/clock/interconnect frameworks, USB role and HCD helpers, platform IRQ naming, runtime/system PM, and QSCRATCH MMIO. Direct `dwc3_core_probe()` integration avoids a child platform device and lets glue callbacks run inside core role/run-stop paths.

Risks: host detection and speed reading still inspect xHCI/root-hub state, so timing around role changes and suspend matters. Resource splitting assumes SDM845-style QSCRATCH offset/size. Wake IRQ polarity is speed-dependent and can misfire if cached speed is stale. VBUS override callback logic is subtle: leaving device role disables override, entering non-device paths can enable it.

Test signals: validate direct core probe/remove, role-switch transitions, gadget run/stop VBUS override, UTMI-as-PIPE operation, one-port and four-port wake IRQ setups, host suspend with LS/FS/HS/no device attached, interconnect bandwidth programming by maximum speed, and system/runtime PM ordering with DWC3 core PM.
