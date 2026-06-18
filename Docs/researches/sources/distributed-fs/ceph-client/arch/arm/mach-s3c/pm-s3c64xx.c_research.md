<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-s3c64xx.c

### Purpose
Implements S3C64xx power domains and suspend-to-RAM CPU/system preparation for legacy board boots.

### Important APIs, Types, And Functions
`struct s3c64xx_pm_domain` wraps a generic PM domain with enable/status bits. `s3c64xx_pd_off()` and `s3c64xx_pd_on()` manipulate `S3C64XX_NORMAL_CFG`. `s3c_pm_save_core()`, `s3c_pm_restore_core()`, `s3c_pm_configure_extint()`, `s3c64xx_cpu_suspend()`, `s3c64xx_pm_prepare()`, and `s3c64xx_pm_init()` implement suspend mechanics and domain registration.

### Control Flow
`s3c64xx_pm_initcall()` sets generic PM callbacks for S3C64xx. Board init calls `s3c64xx_pm_init()`, which initializes common PM and registers always-on and controllable genpd domains. On suspend, the common PM path saves registers, syncs wake masks, writes the resume address to `INFORM0`, clears wake status, configures WFI as sleep, drains write buffers, and executes the low-power instruction.

### State, Persistence, And Dependencies
State includes saved register arrays, `pm_cpu_prep`, `pm_cpu_sleep`, PM domain registration, wake masks, and system controller registers. It depends on `pm.c`, `pm-common.c`, wake-mask helpers, S3C64xx register headers, generic PM domains, and CPU resume assembly.

### Integration Points
Used by Cragganmore and other non-DT S3C64xx boards. It adds the framebuffer device to the F power domain when available.

### Risks
Power-domain status polling can time out. Wake mask synchronization must avoid masking all wake sources. Resume address and register restore order are hardware-critical. DT systems bypass much of this path.

### Test Signals
Power-domain on/off tests, framebuffer domain association, suspend/resume cycles, RTC/touch/SD wake events, and PM debug register checks validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pm-s3c64xx.c -->
