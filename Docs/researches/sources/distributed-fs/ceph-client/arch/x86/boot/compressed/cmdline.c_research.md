## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/cmdline.c

### Purpose
`compressed/cmdline.c` adapts the real-mode command-line parser for the compressed-kernel environment where the full 64-bit command-line pointer can be directly dereferenced through identity mappings.

### Important APIs, Types, And Functions
It defines a local `set_fs()`/`rdfs8()` shim, includes `../cmdline.c`, and exports `get_cmd_line_ptr()`, `cmdline_find_option()`, and `cmdline_find_option_bool()`.

### Control Flow
`get_cmd_line_ptr()` combines `hdr.cmd_line_ptr` with `ext_cmd_line_ptr`. Parser wrappers pass that full pointer to the shared parser. The local FS model turns segment values into linear base addresses so the included parser can run unchanged.

### State, Persistence, And Dependencies
The file is stateless except for a static `fs` base used during parsing. It depends on `boot_params_ptr`, identity mappings for command-line memory, and the shared parser implementation.

### Integration Points
KASLR, ACPI, memory encryption, early console, and other compressed boot code call these wrappers before the real kernel command-line parser is available.

### Risks
The included parser still has a 64 KiB segment-window loop style. The command-line memory must already be mapped before parsing; `ident_map_64.c` later explicitly maps it for the uncompressed kernel.

### Test Signals
Boot with command lines above 4 GiB on x86_64, extended command-line pointer set, absent command line, repeated options, and options consumed by KASLR or ACPI.
