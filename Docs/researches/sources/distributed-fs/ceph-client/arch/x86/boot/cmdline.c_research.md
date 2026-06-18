## sources/distributed-fs/ceph-client/arch/x86/boot/cmdline.c

### Purpose
`cmdline.c` implements the minimal command-line parser used by real-mode setup and reused by compressed boot with a different segment access shim.

### Important APIs, Types, And Functions
The exported functions are `__cmdline_find_option()` and `__cmdline_find_option_bool()`. The local helper is `myisspace()`. Public inline wrappers in `boot.h` and compressed `cmdline.c` call these internals.

### Control Flow
`__cmdline_find_option()` walks a NUL-terminated command line through FS-relative reads, using a state machine for word start, option comparison, skip, and value copy. Repeated `option=value` instances return the last argument length while truncating the copied buffer safely. `__cmdline_find_option_bool()` walks words similarly and returns the one-based starting position of an exact boolean option or zero when absent.

### State, Persistence, And Dependencies
The parser is stateless except for the caller buffer. It depends on `set_fs()` and `rdfs8()` to read command-line bytes and stops at a 64 KiB segment boundary.

### Integration Points
Real-mode setup uses it for options such as serial/video/CPU behavior. The compressed boot version includes this same file after redefining FS access so KASLR, ACPI, memory encryption, and other early logic can parse the full boot command line.

### Risks
No quoting or escaping is supported; whitespace separates tokens. Real-mode callers cannot parse command lines located above 1 MiB through the `boot.h` wrappers. The non-boolean parser deliberately returns the last instance, so callers must expect override behavior.

### Test Signals
Test absent command lines, boolean exact matches, prefix mismatches, repeated `key=value`, truncated buffers with correct returned length, whitespace edge cases, and 64 KiB boundary termination.
