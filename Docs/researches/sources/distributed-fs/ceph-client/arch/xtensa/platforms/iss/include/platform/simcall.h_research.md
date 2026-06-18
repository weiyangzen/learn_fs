# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall.h

Purpose: Provides common inline wrappers for ISS simulator host services independent of the selected backend ABI.

Important APIs, types, and functions: Includes `simcall-iss.h` or `simcall-gdbio.h`; wrappers `simc_exit`, `simc_open`, `simc_close`, `simc_ioctl`, `simc_read`, `simc_write`, `simc_poll`, `simc_lseek`, `simc_argc`, `simc_argv_size`, and `simc_argv`.

Control flow: Each wrapper invokes `__simc()` with backend-defined service numbers. Optional services compile to `WARN_ONCE()` plus failure defaults when the selected backend lacks the service.

State and persistence: Wrapper calls may update backend-local `errno` and host-side file/device state.

Dependencies and integration: Central dependency for ISS platform setup, console, network, and simdisk. Requires exactly one compatible simcall backend config for useful operation.

Risks: Pointer arguments are cast to `int`, matching 32-bit Xtensa assumptions; unsupported wrappers fail at runtime with warnings; backend differences affect register ABI and service availability.

Test signals: Build both simcall backend variants, run ISS console/file/network/simdisk operations, and verify warnings for unsupported services.
