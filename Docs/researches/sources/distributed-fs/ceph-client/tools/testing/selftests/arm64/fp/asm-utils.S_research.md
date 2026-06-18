# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/asm-utils.S

Purpose: reusable freestanding assembly utility routines for arm64 FP/SVE/SME tests.

Important APIs/types/functions: functions `putc`, `puts`, `putdec`, `putdecn`, `puthexb`, `puthexnibble`, `dumphex`, `memcpy`, `memfill_ae`, `memclr`, and `memfill`.

Control flow: output helpers use raw `__NR_write` syscalls to stdout; numeric formatting uses division/modulo loops; memory helpers perform bytewise copy/fill loops.

State and persistence: writes only to stdout or caller-provided memory buffers.

Dependencies/integration: includes `assembler.h` for `function` macros and `<asm/unistd.h>` for syscall numbers. Linked into multiple FP/SVE/SME freestanding tests.

Risks and test signals: intentionally minimal implementations may clobber documented registers only; tests relying on additional preservation would be buggy. Output helpers bypass libc and errno.
