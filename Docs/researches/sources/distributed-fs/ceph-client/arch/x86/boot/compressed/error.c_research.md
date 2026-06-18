## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/error.c

### Purpose
`compressed/error.c` centralizes fatal and warning reporting for compressed boot code.

### Important APIs, Types, And Functions
Exports are `warn()`, `error()`, and, when `CONFIG_EFI_STUB` is enabled, `panic()`.

### Control Flow
`warn()` prints blank lines, the message, and more spacing using `error_putstr()`. `error()` prints the warning, appends `-- System halted`, then halts forever with `hlt`. `panic()` formats a message with EFI libstub `vsnprintf()`, trims a trailing newline, and calls `error()`.

### State, Persistence, And Dependencies
There is no mutable state. Output goes through `misc.c` print routines, which may target serial and/or video. `panic()` depends on EFI stub formatting support.

### Integration Points
Compressed boot modules call `error()` for unrecoverable decompression, mapping, firmware, or memory-acceptance failures and `warn()` for degraded paths such as disabled KASLR.

### Risks
`error()` never returns, so callers must only use it for fatal states. Output availability depends on early console and video initialization state.

### Test Signals
Force invalid ELF, bad relocation, KASLR placement failure warnings, EFI panic formatting, and verify halt behavior and output routing.
