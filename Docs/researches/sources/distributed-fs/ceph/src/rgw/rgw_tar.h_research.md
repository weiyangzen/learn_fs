# sources/distributed-fs/ceph/src/rgw/rgw_tar.h

## Purpose
`rgw_tar.h` provides a lightweight TAR block interpreter for RGW code that reads tar streams.

## Important APIs, Types, and Functions
`BLOCK_SIZE` is 512. `StatusIndicator` tracks whether the current block is empty and whether two consecutive empty blocks mark EOF. `FileType` distinguishes unknown, normal file, and directory. `HeaderView` overlays a 512-byte tar header and exposes file type, filename, and octal file size. `interpret_block()` returns updated status and an optional header view.

## Control Flow
Callers initialize `StatusIndicator::create()`, feed 512-byte bufferlists to `interpret_block()`, and stop when `status.eof()` becomes true. Nonzero blocks produce a `HeaderView`; zero blocks produce no header and update EOF state.

## State and Persistence Behavior
No persistence. `HeaderView` references the caller's buffer memory, so it is only valid while that buffer lives.

## Dependencies and Integration Points
Uses Ceph bufferlist, Boost optional, reversed range adaptor, and standard string utilities. It can support bulk import/export or archive parsing code.

## Risks
`interpret_block()` assumes `bl.c_str()` references at least 512 bytes. Octal parsing does not validate that all characters are octal digits. `HeaderView` uses `strlen()` on fixed-width filename data, which relies on null termination within the field.

## Test Signals
Cover normal file, directory, unknown type, exact zero-block EOF sequence, padded octal sizes, malformed size bytes, non-null-terminated filenames, and undersized input defense at caller level.
