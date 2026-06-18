# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/Makefile

Purpose: builds the standalone powerpc64 endian-switch syscall test and generates reversed-endian instruction bytes for part of the executable.

Important APIs/types/functions: `TEST_GEN_PROGS := switch_endian_test`; `EXTRA_CLEAN` includes generated object and `check-reversed.S`; `ASFLAGS` use `-nostdlib -m64`.

Control flow: `check.o` is converted with `objcopy --reverse-bytes=4` to a binary blob, then `hexdump` emits `.byte` directives into `check-reversed.S`. `switch_endian_test.S` includes that generated file so instructions execute correctly after endianness flips.

State and persistence behavior: generated intermediate files live under `$(OUTPUT)`.

Dependencies and integration points: depends on `objcopy`, `hexdump`, assembler support, kselftest `lib.mk`, and powerpc flags.

Risks and test signals: if byte reversal generation is wrong, the runtime test exits failure or hits illegal instructions. The test is intentionally low-level and does not link libc.
