<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-platform.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-platform.c

Purpose: is the ACPI/platform front-end for Intel LPSS PWM controllers. It maps a platform resource, selects board info from ACPI IDs or platform data, and delegates to the shared LPSS PWM core.

Important APIs/types/functions: `pwm_lpss_probe_platform()` resolves `struct pwm_lpss_boardinfo`, maps resource 0 with `devm_platform_ioremap_resource()`, and calls `devm_pwm_lpss_probe()`. The ACPI table maps `80860F09`, `80862288`, and `80862289` to LPSS variants.

Control flow: platform probe prefers ACPI match data when an ACPI companion exists, otherwise uses `dev_get_platdata()`. After MMIO mapping, all PWM registration and runtime behavior are handled by `pwm-lpss.c`.

State and persistence: no local PWM state is stored here. The shared LPSS core stores register base and boardinfo in its chip-private structure.

Dependencies and integration: depends on platform bus, ACPI matching, LPSS shared exports in namespace `PWM_LPSS`, and PWM core indirectly through `devm_pwm_lpss_probe()`.

Risks and test signals: missing platform data on non-ACPI devices returns `-ENODEV`. Test ACPI and platform-data probe paths, resource-map failures, ID mapping, and module namespace/import behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-platform.c -->
