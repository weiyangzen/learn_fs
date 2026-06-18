# sources/compression/xz/src/common/tuklib_physmem.c

Purpose: implements `tuklib_physmem()`, a portability helper that returns total physical RAM in bytes for many operating systems, or zero when unavailable.

Important APIs/types/functions: exports `uint64_t tuklib_physmem(void)` through the symbol-prefixing macro in `tuklib_physmem.h`. The implementation is a compile-time OS/backend switch covering Windows/Cygwin `GlobalMemoryStatusEx`, OS/2 `DosQuerySysInfo`, DJGPP DPMI, VMS `LIB$GETSYI`, Amiga/AROS `AvailMem`, QNX syspage `asinfo`, AIX `_system_configuration.physmem`, POSIX `sysconf`, BSD `sysctl`, Tru64 `getsysinfo`, HP-UX `pstat_getstatic`, IRIX inventory, and Linux `sysinfo`.

Control flow: the function initializes `ret` to zero, executes exactly one backend selected by preprocessor defines, converts the platform result to bytes, and returns `ret`. Some backends multiply page counts or kilobytes by page size; QNX sums all `asinfo` entries named `ram`; sysctl accepts either 32-bit or 64-bit results.

State and persistence: stateless and side-effect light. It reads kernel/system metadata only; no caches, heap allocation, or persistent handles are kept.

Dependencies/integration: built into liblzma via `src/liblzma/Makefile.am` with `-DTUKLIB_SYMBOL_PREFIX=lzma_`, then wrapped by `src/liblzma/common/hardware_physmem.c` as public `lzma_physmem()`. The xz CLI uses `lzma_physmem()` to choose memory limits and thread policies.

Risks: correctness depends on configure selecting the right backend macros and on platform APIs returning total RAM semantics compatible with xz's resource-limit decisions. Multiplications must stay in `uint64_t`; legacy or unusual systems can fail and yield zero. The Cygwin path deliberately avoids old `sysconf()` behavior. QNX sums ranges and could double count if system metadata semantics changed.

Test signals: `tests/test_hardware.c` calls `lzma_physmem()` and treats zero as skip-like diagnostic rather than hard failure. CLI resource-limit behavior in `src/xz/hardware.c` indirectly exercises the integration.
