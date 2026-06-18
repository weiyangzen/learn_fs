# sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.c

### Purpose
`pm.c` provides a minimal syscore PM hook for Ingenic CGU drivers. It sets the CGU low-power mode bit during suspend and clears it during resume when sleep PM is enabled.

### Important APIs, Types, And Functions
The exported entry point is `ingenic_cgu_register_syscore()`. Internal pieces are `ingenic_cgu_pm_suspend()`, `ingenic_cgu_pm_resume()`, `ingenic_cgu_pm_ops`, and `ingenic_cgu_pm`. The hardware state touched is `CGU_REG_LCR` bit `LCR_LOW_POWER_MODE`.

### Control Flow, State, And Persistence
Each SoC CGU init calls `ingenic_cgu_register_syscore(cgu)`. If `CONFIG_PM_SLEEP` is enabled, the function stores the CGU base in a global pointer and registers syscore ops. Suspend reads LCR and ORs in low-power mode; resume reads LCR and clears the bit. No broad clock register save/restore is done here.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `struct ingenic_cgu`, MMIO accessors, syscore PM, and SoC files calling it after mapping the CGU. Risks include the single global base assuming only one CGU, concurrent or repeated registration, and low-power bit semantics being shared across SoCs. Test signals include suspend/resume on each supported Ingenic SoC, verifying LCR bit transitions, and ensuring clocks remain functional after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/pm.c -->
