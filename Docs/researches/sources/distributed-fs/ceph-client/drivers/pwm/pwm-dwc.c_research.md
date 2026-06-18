# sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc.c

Purpose: implements the PCI frontend for Synopsys DesignWare PWM controllers, currently matching Intel Elkhart Lake hardware.

Important APIs/types/functions: `struct dwc_pwm_info` data for Elkhart Lake describes two 4 KiB controller blocks. `dwc_pwm_init_one()` allocates a shared-core chip and assigns the per-block base address. `dwc_pwm_probe()` enables the PCI device, maps BAR0, creates all PWM chips, stores driver data, and enables runtime PM. Suspend/resume save and restore every timer's load and control registers.

Control flow: PCI probe uses managed PCI enable and iomap helpers, then loops over controller instances. Remove forbids runtime PM and wakes the device. Suspend refuses to proceed if any PWM state is enabled, otherwise snapshots context; resume restores registers for each chip and timer.

State and persistence: `dwc_pwm_drvdata` stores frontend info, BAR base, and chip pointers. `dwc->ctx[]` persists timer registers across system sleep only. Runtime PM state is delegated to the device core.

Dependencies and integration: depends on PCI, managed MMIO mapping, runtime PM, the `pwm-dwc-core.c` exported allocator, and Intel PCI device id `0x4bb7`.

Risks and test signals: suspend rejects active consumers with `-EBUSY`, which can block system suspend. The source defines `DEFAULT_MOUDLE_NAMESPACE` with a typo, while namespace import is handled in the header. Test signals include PCI probe with two chips, BAR mapping failure, active-PWM suspend rejection, inactive context restore, runtime PM transitions, and module namespace/link checks.
