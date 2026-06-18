# sources/distributed-fs/ceph-client/lib/xz/xz_stream.h

## Purpose
Defines `.xz` stream/container constants and integrity-check identifiers used by `xz_dec_stream.c`.

## APIs and control flow
Defines `STREAM_HEADER_SIZE`, header/footer magic strings and sizes, `vli_type`, `VLI_MAX`, `VLI_UNKNOWN`, `VLI_BYTES_MAX`, `enum xz_check`, and `XZ_CHECK_MAX`. In kernel builds without internal CRC32, it maps `xz_crc32` to the kernel `crc32_le` helper using the complement convention expected by XZ.

## State, dependencies, and integration
The header has constants/type aliases only. Runtime VLI and check state lives in the stream decoder. It depends on `linux/crc32.h` when the kernel CRC implementation is selected and on the `.xz` file format values.

## Risks and test signals
Changing magic bytes, VLI limits, or check IDs breaks format compatibility. A 32-bit `vli_type` is documented as size-limiting and experimental. Tests should cover header/footer validation, VLI boundary cases, check type handling, and builds with internal versus kernel CRC32.
