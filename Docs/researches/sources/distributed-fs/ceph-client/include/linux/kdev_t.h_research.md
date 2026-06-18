# sources/distributed-fs/ceph-client/include/linux/kdev_t.h

## Purpose
Defines kernel helpers for encoding, decoding, formatting, and validating device numbers (`dev_t`) across old, new, huge, and SysV filesystem formats.

## Important APIs, Types, And Functions
`MINORBITS`, `MINORMASK`, `MAJOR()`, `MINOR()`, and `MKDEV()` define the in-kernel major/minor packing. Formatting helpers are `print_dev_t()` and `format_dev_t()`. Encoding helpers include `old_valid_dev()`, `old_encode_dev()`, `old_decode_dev()`, `new_encode_dev()`, `new_decode_dev()`, `huge_encode_dev()`, `huge_decode_dev()`, `sysv_valid_dev()`, `sysv_encode_dev()`, `sysv_major()`, and `sysv_minor()`.

## Control Flow
All helpers are inline arithmetic. Old format uses 8-bit major and minor fields. New format preserves low minor bits, packs major in the middle, and carries high minor bits above. SysV uses a 14-bit major and 18-bit minor.

## State And Persistence
No runtime state is stored. Encoded values persist in filesystem metadata or user-visible strings depending on caller.

## Dependencies And Integration Points
Includes `uapi/linux/kdev_t.h`. Integrates with VFS, block/char device registration, filesystem on-disk inode formats, proc/sysfs formatting, and legacy compatibility.

## Risks
Encoding a device number into a format that cannot represent it truncates or rejects information depending on caller. `print_dev_t()` includes a trailing newline while `format_dev_t()` does not. Callers must size buffers for `major:minor`.

## Test Signals
Tests should cover encode/decode round trips for boundary majors/minors, invalid old/SysV values, formatting output, and filesystem compatibility paths.
