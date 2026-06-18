# sources/distributed-fs/ceph-client/include/uapi/linux/param.h

Purpose: Provides the generic UAPI include wrapper for architecture-specific system parameter constants.

Important APIs/types/functions: Includes `<asm/param.h>`, which typically provides constants such as `HZ`, `EXEC_PAGESIZE`, `NOGROUP`, and related architecture values.

Control flow: No runtime flow. Userspace includes `<linux/param.h>` and receives the architecture's exported parameter definitions through the asm UAPI layer.

State and persistence behavior: No state. Values are compile-time constants that describe kernel/userspace ABI assumptions for the target architecture.

Dependencies and integration points: Integrates directly with per-architecture UAPI headers and libc/kernel-header consumers.

Risks: Architecture mismatches or stale installed headers can produce incorrect constants in userspace. This wrapper must remain minimal to avoid diverging from `asm/param.h`.

Test signals: Compile on each supported architecture, compare exported constants with the target asm UAPI, and ensure userspace packages can include the header without kernel-only dependencies.
