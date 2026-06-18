# sources/distributed-fs/ceph-client/lib/xz/Kconfig

## Purpose
Defines configuration for the in-kernel XZ decompressor, optional architecture BCJ filters, MicroLZMA support, and a developer test module.

## Options and control flow
`XZ_DEC` is the main tristate and selects `CRC32`. Under `if XZ_DEC`, architecture filters `XZ_DEC_X86`, `XZ_DEC_POWERPC`, `XZ_DEC_ARM`, `XZ_DEC_ARMTHUMB`, `XZ_DEC_ARM64`, `XZ_DEC_SPARC`, and `XZ_DEC_RISCV` default to yes for expert-tunable BCJ support and select hidden `XZ_DEC_BCJ`. `XZ_DEC_MICROLZMA` enables the compact MicroLZMA header variant. `XZ_DEC_TEST` depends on `XZ_DEC` and builds the character-device tester.

## State, dependencies, and integration
Choices persist in `.config` and become `CONFIG_XZ_DEC_*` symbols consumed by `lib/xz/Makefile` and mapped to internal macros in `xz_private.h`.

## Risks and test signals
Disabling a needed BCJ filter makes valid streams fail with `XZ_OPTIONS_ERROR`. `XZ_DEC_TEST` should stay off outside decoder development. Build tests should cover built-in/module/off states, each BCJ toggle, MicroLZMA, and the test module; runtime tests should decode streams using every enabled filter and reject unsupported filters cleanly.
