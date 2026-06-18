# sources/distributed-fs/ceph-client/lib/xz/Makefile

## Purpose
Connects XZ decoder source objects to Kconfig selections in Kbuild.

## Build flow
`obj-$(CONFIG_XZ_DEC) += xz_dec.o` builds the composite decoder. `xz_dec-y` always includes `xz_dec_syms.o`, `xz_dec_stream.o`, and `xz_dec_lzma2.o`; `xz_dec-$(CONFIG_XZ_DEC_BCJ)` conditionally includes `xz_dec_bcj.o`. `obj-$(CONFIG_XZ_DEC_TEST) += xz_dec_test.o` builds the optional tester separately.

## State, dependencies, and integration
There is no runtime state. The file integrates `lib/xz/Kconfig` with the module/export code in `xz_dec_syms.c` and the decoder implementations.

## Risks and test signals
Omitting `xz_dec_bcj.o` causes BCJ streams to be unsupported. Object composition must preserve exported APIs. Build tests should verify object inclusion for `CONFIG_XZ_DEC=y/m`, `CONFIG_XZ_DEC_BCJ=y`, and `CONFIG_XZ_DEC_TEST=m`, plus link/modpost resolution of decoder symbols.
