# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpu.h

Purpose: Samsung CPU ID helpers and init declarations.

Important APIs/types/functions: defines CPU ID/mask constants, `IS_SAMSUNG_CPU()` macro, inline `is_samsung_s3c6400()`, `is_samsung_s3c6410()`, `soc_is_s3c64xx()` family macros, `struct cpu_table`, and declarations for CPU/UART/subsystem init.

Control flow: inline helpers compare `samsung_cpu_id` with masks; other declarations are implemented elsewhere.

State and persistence: reads global `samsung_cpu_id`.

Dependencies and integration points: used across S3C GPIO, cpuidle, init, and board setup to gate SoC-specific behavior.

Risks: helpers return zero if CPU config symbols are absent, so code can compile but skip runtime paths. ID masks must match hardware.

Test signals: CPU ID detection and conditional paths for S3C6400/S3C6410.
