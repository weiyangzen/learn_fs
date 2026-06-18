<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core-s3c64xx.h

### Purpose
Provides S3C64xx-specific inline hooks and wake-mask constants used by generic Samsung PM code.

### Important APIs, Types, And Functions
Inline hooks include `s3c_pm_debug_init_uart()`, `s3c_pm_arch_prepare_irqs()`, `s3c_pm_arch_stop_clocks()`, `s3c_pm_arch_show_resume_irqs()`, `s3c_pm_restored_gpios()`, and `samsung_pm_saved_gpios()`. `s3c_irqwake_eintallow` and `s3c_irqwake_intallow` define wake-capable IRQ masks when sleep support is enabled.

### Control Flow
The generic PM path calls these architecture hooks around suspend/resume phases. Most are no-ops for S3C64xx except GPIO save/restore notification hooks and wake mask constants.

### State, Persistence, And Dependencies
No direct state. It depends on PM sleep configuration and GPIO PM helpers.

### Integration Points
Included through the PM core wrapper selected for S3C64xx.

### Risks
No-op hooks mean any required hardware-specific preparation must live elsewhere. Wake-mask constants must match hardware wake capability.

### Test Signals
Suspend with selected external and internal wake sources validates allowed masks and hook ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-core-s3c64xx.h -->
