<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/Makefile

## Purpose
This makefile maps SPARC crypto Kconfig symbols to accelerated crypto objects.

## Important APIs, Types, and Functions
`aes_sparc64-y` contains `aes_asm.o` and `aes_glue.o`; `camellia_sparc64-y` contains `camellia_asm.o` and `camellia_glue.o`. `obj-$(CONFIG_CRYPTO_AES_SPARC64)` and `obj-$(CONFIG_CRYPTO_CAMELLIA_SPARC64)` emit the corresponding modules/built-ins.

## Control Flow
Kbuild compiles the assembly and C glue together only when the matching config symbol is enabled.

## State and Persistence Behavior
No runtime state exists here; it controls build artifacts.

## Dependencies and Integration Points
It depends on Kbuild composite object naming and the crypto Kconfig symbols. It links opcode assembly entry points with crypto API glue.

## Risks
Object ordering and naming must match module names and extern declarations. Omitting either assembly or glue object breaks linkage.

## Test Signals
Build both crypto options as modules and built-ins, then run `modinfo`, load modules, and execute crypto selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/Makefile -->
