# sources/cloud-native/ostree/src/libostree/ostree-lzma-common.c

## Purpose
This file translates liblzma return codes into GLib `GConverterResult` values and `GError`s shared by OSTree's LZMA compressor and decompressor.

## Important APIs and Control Flow
`_ostree_lzma_return(lzma_ret res, GError **error)` maps `LZMA_OK` to `G_CONVERTER_CONVERTED`, `LZMA_STREAM_END` to `G_CONVERTER_FINISHED`, and every known error to `G_CONVERTER_ERROR` with a specific `G_IO_ERROR` message. `LZMA_BUF_ERROR` is mapped to `G_IO_ERROR_PARTIAL_INPUT`; memory, format, options, data, and check errors are mapped to failed converter errors.

## State, Dependencies, Integration, Risks, and Tests
The function is stateless. Dependencies are liblzma, GLib/GIO, errno/string headers, and the shared header. Compressor/decompressor implementations rely on this mapping for all terminal results. Risks are semantic mismatch between liblzma's `LZMA_BUF_ERROR` and GLib callers' expectations, and loss of numeric lzma code details. Test signals should exercise each mapped error, stream end, and normal converted return.
