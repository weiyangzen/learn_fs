# sources/control-plane/longhorn-engine/pkg/qcow/libqcow.go

Purpose: wraps `libqcow` through cgo to provide read-only QCOW image access as a Longhorn diff-disk-like object.

Important APIs/types/functions: `Qcow` holds a `*C.libqcow_file_t`. `Open` initializes and opens a path with `LIBQCOW_OPEN_READ`. `toError` converts libqcow errors into Go errors. `ReadAt` calls `libqcow_file_read_buffer_at_offset`. `Size` calls `libqcow_file_get_media_size`. `Close` closes the file. `WriteAt`, `UnmapAt`, and `Fd` are unsupported/no-op for write-oriented integration.

Control flow: open initializes then opens, freeing the libqcow handle on open failure. Reads return `io.EOF` for zero bytes, convert negative return values to libqcow errors, and otherwise return the byte count.

State and persistence: the wrapper owns a native file handle. It does not write or persist Longhorn metadata.

Dependencies and integration points: links against `-lqcow -lz -pthread` and imports `libqcow.h`. Intended for backing or image layers that need `ReadAt`, `Size`, and `Close`.

Risks: `ReadAt` uses `&buf[0]` and will panic on zero-length buffers. `Close` does not free the libqcow file handle after close, which may leak native resources depending on libqcow expectations. Unsupported write/unmap make it unsuitable as an active layer. C library availability is a build/runtime requirement.

Test signals: no direct tests. Unit tests would need libqcow fixtures and should cover zero-length read, EOF, size, and close/free behavior.
