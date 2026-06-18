# File Research: sources/cow-pools/bcachefs-tools/include/linux/mm.h

This header supplies minimal memory-management compatibility. It defines a `struct sysinfo` layout compatible with the Linux `SYS_sysinfo` syscall, including padding needed on 32-bit builds.

`si_meminfo()` calls `syscall(SYS_sysinfo)` and asserts success. `_totalram_pages` is declared externally, `totalram_pages()` returns it, and `si_mem_available()` computes available pages from `freeram * mem_unit`. `mem_alloc_profiling_enabled()` always returns false.
