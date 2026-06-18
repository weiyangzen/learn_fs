# sources/distributed-fs/ceph-client/drivers/soc/versatile/soc-integrator.c

## Purpose
This built-in init file registers SoC bus information for ARM Integrator core modules. It reads the core module ID from a syscon regmap, decodes manufacturer, architecture, FPGA, build, and revision information, and exposes custom sysfs attributes.

## Important APIs, Types, And Functions
Important functions are `integrator_arch_str`, `integrator_fpga_str`, attribute show handlers, and `integrator_soc_init`. The global `integrator_coreid` backs sysfs attributes. The OF match is `arm,core-module-integrator`.

## Control Flow
At `device_initcall`, the driver finds the matching core-module node, converts it to a regmap, reads offset 0, allocates `soc_device_attribute`, fills `soc_id`, `machine`, `family`, and custom attribute group, registers the SoC device, then logs decoded fields.

## State And Persistence
`integrator_coreid` stores the decoded raw ID for attribute reads. The SoC device persists after init. The syscon register is read-only platform identity state.

## Dependencies And Integration Points
It depends on OF, syscon/regmap, SoC bus, and Integrator platform DT. It is built by `SOC_INTEGRATOR_CM`.

## Risks And Test Signals
Risks include failure to unregister on later errors, generic `-ENODEV` returns obscuring causes, and unknown architecture/FPGA values. Test signals include boot logs with decoded core module fields and sysfs attributes `manufacturer`, `arch`, `fpga`, and `build`.
