<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.h -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.h

Purpose: declares the shared Intel LPSS PWM core interface consumed by the PCI and platform wrapper drivers.

Important APIs/types/functions: `LPSS_MAX_PWMS` defines the maximum channel count. `struct pwm_lpss_boardinfo` carries per-family clock rate, channel count, base-unit bit width, fixed base-unit value, and bypass flag. It declares exported descriptors for BYT, BSW, BXT, and TNG plus `devm_pwm_lpss_probe()` and `pwm_lpss_remove()`.

Control flow: the header has no runtime control flow; it defines the contract wrappers use to instantiate the common core.

State and persistence: boardinfo data is immutable configuration state. Runtime state is owned by `pwm-lpss.c`.

Dependencies and integration: includes device, IO, and PWM declarations and bridges `pwm-lpss-pci.c`, `pwm-lpss-platform.c`, and `pwm-lpss.c`.

Risks and test signals: interface drift between wrappers and core is the main risk. Compile tests should cover modular builds and namespace import users, plus all boardinfo symbols referenced by PCI/ACPI tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.h -->
