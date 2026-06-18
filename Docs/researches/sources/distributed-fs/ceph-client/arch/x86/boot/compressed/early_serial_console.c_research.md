## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/early_serial_console.c

### Purpose
`compressed/early_serial_console.c` reuses the setup early serial console implementation while placing `early_serial_base` in `.data` so it is available before BSS is cleared.

### Important APIs, Types, And Functions
It defines `int early_serial_base __section(".data")` and includes `../early_serial_console.c`, which provides `console_init()` and serial command-line parsing.

### Control Flow
The included setup implementation parses early serial options and initializes the base port. Compressed `misc.c` later uses `early_serial_base` in `__putstr()` to send debug and error output.

### State, Persistence, And Dependencies
Persistent state is the chosen serial I/O base address. It depends on command-line parsing, port I/O, and early boot `.data` survival before BSS initialization.

### Integration Points
Built only when `CONFIG_EARLY_PRINTK` is selected. It feeds compressed boot diagnostics, including decompression, KASLR, ACPI, and error paths.

### Risks
Incorrect base-port detection can hang or delay output loops. Because BSS clearing happens during startup relocation, state that must survive initial output has to be in `.data`, as this wrapper enforces.

### Test Signals
Boot with early serial enabled and disabled, valid and invalid serial options, and verify decompressor messages appear over serial before and after BSS clearing.
