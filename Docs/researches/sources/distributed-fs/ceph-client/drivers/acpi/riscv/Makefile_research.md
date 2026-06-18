## sources/distributed-fs/ceph-client/drivers/acpi/riscv/Makefile

### Purpose
`riscv/Makefile` selects the RISC-V ACPI object files compiled into the kernel.

### Important APIs, Types, And Functions
It always builds `rhct.o`, `init.o`, and `irq.o`; conditionally builds `cpuidle.o` under `CONFIG_ACPI_PROCESSOR_IDLE`, `cppc.o` under `CONFIG_ACPI_CPPC_LIB`, and `rimt.o` under `CONFIG_ACPI_RIMT`.

### Control Flow
There is no runtime control flow. Build-time configuration determines which RISC-V ACPI capabilities are present.

### State, Persistence, And Dependencies
State is the kernel build graph. Dependencies are the corresponding Kconfig symbols and object files.

### Integration Points
The Makefile connects generic ACPI processor idle and CPPC options to RISC-V-specific FFH implementations, and connects `ACPI_RIMT` to IOMMU table support.

### Risks
Missing config symbols omit architecture hooks that generic ACPI code may weakly fall back from. Always-built `init.o`, `irq.o`, and `rhct.o` assume RISC-V ACPI core support is being compiled.

### Test Signals
Build matrix tests should cover idle on/off, CPPC on/off, RIMT on/off, and ensure unresolved symbols do not appear when optional files are omitted.
