<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/axp20x-pek.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/axp20x-pek.c

Purpose: power enable key input and timing sysfs driver for X-Powers AXP20x/AXP221-family PMICs.

Important APIs/types/functions: `struct axp20x_pek` stores parent MFD, input, timing info, and rising/falling IRQs. `axp20x_pek_irq()` maps `PEK_DBF` to KEY_POWER down and `PEK_DBR` to release. Sysfs `startup` and `shutdown` show/store nearest supported timing values through `AXP20X_PEK_KEY`. PM ops manage IRQ wake and AXP288 resume-noirq interrupt clearing.

Control flow and state: probe allocates state, optionally registers input depending on AXP288/Cherry Trail duplicate-button detection, selects timing table from platform ID, and exposes attributes. Input setup converts regmap IRQ IDs to virtual IRQs and requests both edges.

State and persistence behavior: hardware PEK timing values persist in PMIC registers. Runtime state tracks IRQ numbers and selected timing table. Wakeup capability is enabled for the platform device.

Dependencies and integration points: depends on AXP20x MFD/regmap IRQ controller, ACPI duplicate-button detection helpers, Linux input, sysfs attribute groups, and PM wake APIs.

Risks: if input registration is skipped, suspend/resume still assumes IRQ fields are valid, which depends on platform path expectations. Store rounds requested times to nearest supported value, which may surprise users. Regmap update errors are returned as `-EINVAL`, losing detail.

Test signals: test AXP20x and AXP221 timing maps, sysfs round-trip values, press/release IRQs, AXP288 duplicate suppression, suspend wake/non-wake IRQ handling, and AXP288 resume-noirq interrupt clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/axp20x-pek.c -->
