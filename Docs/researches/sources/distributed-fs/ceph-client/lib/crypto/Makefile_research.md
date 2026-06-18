# sources/distributed-fs/ceph-client/lib/crypto/Makefile

## Purpose
This Makefile maps crypto library Kconfig symbols to objects, architecture-specific accelerators, generated perlasm sources, sanitizer exceptions, and clean targets.

## Important APIs, Types, and Functions
It defines build rules for `libaes.o`, `libaescfb.o`, `libaesgcm.o`, `libarc4.o`, `libblake2b.o`, always-built `blake2s.o` and `chacha-block-generic.o`, `libchacha.o`, and many other crypto libraries. It defines perlasm commands and arch object lists for ARM, ARM64, PPC, RISCV, S390, SPARC, X86, MIPS, and generated clean files.

## Control Flow
Kbuild conditionals append generic objects first, then add arch objects when the corresponding `CONFIG_CRYPTO_LIB_*_ARCH` symbol is enabled. Some objects include `CFLAGS_* += -I$(src)/$(SRCARCH)` so generic C files can include arch-local headers named like `aes.h` or `chacha.h`.

## State and Persistence
Build state is confined to generated object/source files and Kbuild variables. No runtime state exists.

## Dependencies and Integration Points
It is the central integration point between Kconfig and the source files in this subset. It also generates perlasm assembly for PPC, ARM/ARM64, MIPS, RISCV, and x86 crypto routines and marks some generated objects non-standard for objtool/build handling.

## Risks and Test Signals
Risks include wrong arch object inclusion, stale generated assembly flavor, missing clean-file entries, and include-path collisions. Test signals are cross-arch builds with arch acceleration toggled and crypto selftest modules.
