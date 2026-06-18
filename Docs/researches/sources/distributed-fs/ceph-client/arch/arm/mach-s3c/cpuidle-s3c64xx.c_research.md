# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpuidle-s3c64xx.c

Purpose: simple cpuidle driver for S3C64xx that gates the ARM core while keeping the system active.

Important APIs/types/functions: `s3c64xx_enter_idle()`, `s3c64xx_cpuidle_driver`, and `s3c64xx_init_cpuidle()`.

Control flow: device init registers the driver only if `soc_is_s3c64xx()`. Entering idle updates `S3C64XX_PWR_CFG` WFI mode bits to IDLE, calls `cpu_do_idle()`, and returns the selected state index.

State and persistence: mutates S3C64xx power config register. Runtime state is managed by cpuidle core.

Dependencies and integration points: depends on CPU ID helpers, S3C64xx power registers, and ARM idle instruction.

Risks: only one shallow state; wrong PWRCFG bits could enter deeper stop/sleep unexpectedly.

Test signals: cpuidle state registration, idle residency, wake latency, and power config readback.
