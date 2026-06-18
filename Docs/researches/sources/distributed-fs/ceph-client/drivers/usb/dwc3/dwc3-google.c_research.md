# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-google.c

## Purpose
`dwc3-google.c` is a Google LGA DWC3 glue driver. It wraps the core with Google-specific resets, clocks, power-domain links, syscon-controlled host PMU/USB interrupt registers, optional USB2-only programming, and host hibernation wake through PME interrupts.

## Important APIs, Types, and Functions
`struct dwc3_google` embeds `struct dwc3` and stores bulk clocks, four resets, non-sticky reset, power-domain devices/links, notifier, syscon offsets, PME IRQs, and hibernation flags. Key functions are `dwc3_google_pm_domain_init()`, `dwc3_google_pm_domain_deinit()`, `dwc3_google_rst_init()`, `dwc3_google_set_pmu_state()`, `dwc3_google_clear_pme_irqs()`, `dwc3_google_enable_pme_irq()`, `dwc3_google_disable_pme_irq()`, `dwc3_google_resume_irq()`, `dwc3_google_usb_psw_pd_notifier()`, `dwc3_google_probe()`, remove, and PM wrappers.

## Control Flow
Probe attaches `psw` and `top` power domains, registers a genpd notifier for hibernation state changes, creates device links, resolves `google,usb-cfg-csr` syscon offsets, sets USB2-only mode if no `usb3-phy` name exists, enables all clocks, gets/deasserts resets, requests disabled-by-default HS/SS PME IRQs, marks wake capable, and calls `dwc3_core_probe()` with clocks/resets ignored by the core.

Suspend first lets the DWC3 core suspend. If in host mode and runtime suspend or wake-capable system suspend applies, it enters hibernation by holding the top power domain active, enabling wake on it, enabling PME IRQs, and setting `is_hibernation`. The `psw` power-domain notifier moves the PMU to D3 and asserts non-sticky reset on domain off, then clears PME, deasserts reset, and returns PMU to D0 on domain on. Non-hibernation suspend asserts resets and disables clocks. Resume reverses hibernation or reenables clocks/resets and then resumes the core.

## State and Persistence Behavior
Live state includes PM domain links, notifier registration, reset state, syscon PMU state, PME IRQ enable/wake state, and `is_hibernation`. USB2-only configuration may need reprogramming after non-hibernation resume. No disk persistence exists.

## Dependencies and Integration Points
The driver depends on clk bulk APIs, reset bulk APIs, genpd attach/notifier/device links, syscon/regmap, IRQ wake, DWC3 core PM, and platform IRQ/resource lookup. It directly resumes the xHCI child device from the PME IRQ if host hibernation wake is valid.

## Risks
PM sequencing is complex. PME IRQs must only be enabled during hibernation, top/psw power-domain links must avoid unintended power collapse, and PMU D0/D3 polling can time out. Non-sticky reset transitions in the genpd notifier happen while power domains change. USB2-only programming must be restored after resets. Error paths must deinit power domains and assert resets consistently.

## Test Signals
Validate probe with both USB2-only and USB3 PHY configurations, PM domain attach/link behavior, hibernation enter/exit, HS and SS PME wake, xHCI resume on PME, PMU D0/D3 poll success, runtime PM cycles, non-wakeup system suspend that asserts resets/clocks off, and remove while domains and IRQs are registered.
