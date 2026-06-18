# sources/cloud-native/ostree/src/libostree/ostree-lzma-common.h

## Purpose
This private header declares the common liblzma-to-GIO converter result helper used by OSTree LZMA converters.

## Important API, Dependencies, and Integration
It includes GIO and liblzma and declares `GConverterResult _ostree_lzma_return(lzma_ret value, GError **error)`. Both compressor and decompressor call it after initializing or running an `lzma_stream`.

## Risks and Tests
The header exposes a narrow error-conversion contract. Any change in mapping affects all LZMA stream consumers. Compile tests should cover liblzma availability, and behavior tests should ensure converter users receive consistent `G_IO_ERROR` domains and converter result values.
