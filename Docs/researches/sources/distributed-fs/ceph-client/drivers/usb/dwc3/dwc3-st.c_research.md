# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-st.c

Purpose: STMicroelectronics STi DWC3 glue driver. It manages glue registers, syscfg regmap configuration for static host/device mode, powerdown and soft reset controls, child DWC3 population, and sleep-state pinctrl/reset handling.

Important APIs, types, and functions: `struct st_dwc3` stores device, glue MMIO, syscfg regmap, syscfg register offset, `dr_mode`, and reset controls. `st_dwc3_drd_init()` programs static DRD mode into syscfg bits. `st_dwc3_init()` configures clock/reset glue, xHCI revision selection, and VBUS/powerpresent/bvalid muxing. `st_dwc3_probe()`, `_remove()`, `_suspend()`, and `_resume()` own lifecycle.

Control flow: probe maps named `reg-glue`, gets `st,syscfg` regmap and `syscfg-reg` offset, finds the child DWC3 node, deasserts powerdown and softreset controls, populates the child, finds the child platform device to read `dr_mode`, programs static host/device syscfg through `st_dwc3_drd_init()`, initializes glue registers, and stores private data. Suspend asserts resets and selects sleep pinctrl; resume restores default pinctrl, deasserts resets, reruns DRD syscfg, and reruns glue init.

State and persistence: persistent state is static `dr_mode`, reset handles, and register offsets. Hardware state in syscfg and glue registers is restored on resume. OTG/dual-role dynamic switching is not implemented; only host or peripheral static modes are accepted.

Dependencies and integration: depends on MFD syscon/regmap, reset framework, pinctrl PM helpers, OF child population, USB dr_mode helpers, and DWC3 child platform device discovery. It includes DWC3 `core.h`/`io.h` but mainly interacts through child creation.

Risks: unsupported `dr_mode` returns `-EINVAL`, so DT must not request OTG. Bit masking in `st_dwc3_drd_init()` relies on syscfg layout matching `st,stih407-dwc3`. Probe configures DRD after child population, so child behavior during early probe must tolerate wrapper defaults. Reset ordering during suspend/resume is hardware-sensitive.

Test signals: test host and peripheral DT modes, unsupported OTG rejection, syscfg write failures, child discovery failure paths, reset assert/deassert sequencing, glue register values after resume, and pinctrl sleep/default transitions.
