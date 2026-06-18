# sources/compression/zlib/zconf.h

`zconf.h` is zlib's generated/current public configuration header. It defines symbol prefixing, platform detection, calling conventions, export/import attributes, scalar and pointer typedefs, large-file types, feature-detection macros, and compatibility mappings used by `zlib.h` and internal sources.

Important definitions include the `Z_PREFIX` remap for functions/types/structs, platform macros, `z_const`, `z_size_t`, `MAX_MEM_LEVEL`, `MAX_WBITS`, `OF`, `FAR`, `ZEXTERN`, `ZEXPORT`, `ZEXPORTVA`, `Byte`, `Bytef`, `uInt`, `uLong`, `voidp` variants, `z_crc_t`, `z_off_t`, and `z_off64_t`. It conditionally includes standard, Unix, and Windows headers.

The preprocessor flow applies prefixing, normalizes platforms, detects standards support, chooses size and offset types, configures DLL/calling conventions, selects CRC types, and applies MVS pragma maps. There is no runtime state, but the header controls compile-time ABI for zlib and downstream consumers. Risks are ABI breaks from typedef/export/prefix changes, invalid configured expressions, and prefix-list drift. Test signals are successful builds across prefixed, DLL, solo, large-file, and legacy-platform configurations.
