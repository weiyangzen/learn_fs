# sources/compression/xz/src/liblzma/api/lzma/hardware.h

Purpose: declares public hardware-capability helpers used to choose memory and threading limits.

Important APIs/types/functions: exports `lzma_physmem(void)` for total RAM in bytes and `lzma_cputhreads(void)` for available CPU threads/cores.

Control flow: callers invoke these synchronous probes and treat zero as unavailable. The header notes that implementations may temporarily load libraries or open file descriptors and restart interrupted syscalls.

State and persistence: no public state; implementations are wrappers around tuklib helpers and platform APIs.

Dependencies/integration: `lzma_physmem()` wraps `tuklib_physmem()` from this subset; `lzma_cputhreads()` wraps `tuklib_cpucores()`. The xz CLI uses both in `src/xz/hardware.c` for default memory/thread decisions; container docs recommend `lzma_physmem()/4` as a decoder threading memory starting point.

Risks: hardware detection failure must not be fatal. Applications must still impose their own policy; these helpers expose capability, not a safe limit. File descriptor side effects can matter to programs with strict fd assumptions.

Test signals: `tests/test_hardware.c` exercises both functions and tolerates platform inability to report values.
