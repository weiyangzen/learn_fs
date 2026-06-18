# sources/distributed-fs/ceph-client/lib/xz/xz_dec_syms.c

## Purpose
Provides module exports and metadata for the XZ decompressor.

## APIs and control flow
Exports `xz_dec_init`, `xz_dec_reset`, `xz_dec_run`, and `xz_dec_end`. Under `CONFIG_XZ_DEC_MICROLZMA`, it also exports `xz_dec_microlzma_alloc`, `xz_dec_microlzma_reset`, `xz_dec_microlzma_run`, and `xz_dec_microlzma_end`. There is no runtime algorithm; the file is linked into `xz_dec.o` so module/export infrastructure can publish the decoder APIs.

## State, dependencies, and integration
No mutable runtime state. It includes `linux/module.h` and `linux/xz.h` and must match implementations in `xz_dec_stream.c` and `xz_dec_lzma2.c`. Module metadata declares description, version, authors, and dual BSD/GPL license.

## Risks and test signals
Export drift causes build, modpost, or module-consumer failures. MicroLZMA exports must stay conditional. Tests are build/link checks with and without MicroLZMA and module consumers resolving the public symbols.
