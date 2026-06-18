# sources/compression/xz/cmake/tuklib_physmem.cmake

## Purpose
This module detects how tuklib should determine total physical memory and applies compile definitions for the selected method.

## Important APIs and Control Flow
`tuklib_physmem_internal_check()` first handles Windows/Cygwin and other special platforms in C, then probes AIX `_system_configuration.physmem`, POSIX `sysconf(_SC_PAGESIZE/_SC_PHYS_PAGES)`, BSD `sysctl(CTL_HW, HW_PHYSMEM)`, and HP-UX `pstat_getstatic`. `tuklib_physmem(TARGET_OR_ALL)` caches found status and applies `TUKLIB_PHYSMEM_*` and `HAVE_SYS_PARAM_H` definitions.

## State, Dependencies, and Integration
It uses CMake compile checks, include checks, push/pop check state, and `tuklib_common.cmake`. Results drive `src/common/tuklib_physmem.c` and liblzma APIs such as `lzma_physmem()`.

## Risks and Test Signals
The module intentionally lacks some Autotools checks, such as Tru64, IRIX, and Linux `sysinfo()`, preferring `sysconf()` on GNU/Linux. Top-level CMake treats missing detection as an error for expected platforms, so portability workflows are the main signal.
