## sources/distributed-fs/ceph-client/drivers/acpi/riscv/init.h

### Purpose
`riscv/init.h` declares internal RISC-V ACPI initialization hooks shared by the RISC-V ACPI source files.

### Important APIs, Types, And Functions
It declares `riscv_acpi_init_gsi_mapping()` and `riscv_acpi_rimt_init()`.

### Control Flow
There is no runtime control flow in the header.

### State, Persistence, And Dependencies
The header includes `<linux/init.h>` to support `__init` annotations and depends on the matching definitions in `irq.c` and `rimt.c`.

### Integration Points
`init.c` includes this header to call interrupt and RIMT initialization without exporting those functions outside the RISC-V ACPI directory.

### Risks
If optional RIMT compilation and declarations get out of sync, builds can fail. The header intentionally stays narrow, so new initialization hooks need explicit declarations.

### Test Signals
Build with and without `CONFIG_ACPI_RIMT`, and ensure `__init` declarations match definitions.
