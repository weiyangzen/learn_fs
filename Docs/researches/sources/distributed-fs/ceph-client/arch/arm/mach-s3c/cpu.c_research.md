# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpu.c

Purpose: Samsung S3C64xx CPU identification.

Important APIs/types/functions: global `samsung_cpu_id` and `s3c64xx_init_cpu()`.

Control flow: reads CPU ID from `S3C_VA_SYS + 0x118`; if zero, writes/reads the S3C6400 alternate ID register at `0xA1C`. It logs the ID and a deprecation/removal warning.

State and persistence: stores detected ID in global `samsung_cpu_id` for `soc_is_*` helpers. Hardware registers are only read except the S3C6400 enable/write path.

Dependencies and integration points: depends on `map-base.h`, `cpu.h`, and early I/O mapping. GPIO and cpuidle code use `soc_is_s3c64xx()`.

Risks: detection before mapping is valid would fault. The warning is intentionally loud but not fatal.

Test signals: boot log CPU ID, S3C6400 fallback path, and `soc_is_s3c64xx()`-guarded init paths.
