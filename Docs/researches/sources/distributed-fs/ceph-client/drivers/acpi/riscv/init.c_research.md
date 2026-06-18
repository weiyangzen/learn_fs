## sources/distributed-fs/ceph-client/drivers/acpi/riscv/init.c

### Purpose
`riscv/init.c` performs RISC-V ACPI architecture initialization.

### Important APIs, Types, And Functions
The file defines `acpi_arch_init()`.

### Control Flow
During ACPI architecture initialization, it initializes RISC-V GSI mapping with `riscv_acpi_init_gsi_mapping()`. If `CONFIG_ACPI_RIMT` is enabled, it also initializes the cached RIMT table through `riscv_acpi_rimt_init()`.

### State, Persistence, And Dependencies
This file owns no state. It depends on declarations in `init.h` and on the implementations in `irq.c` and optionally `rimt.c`.

### Integration Points
The generic ACPI core invokes `acpi_arch_init()` so RISC-V interrupt-controller and IOMMU table discovery are ready before ACPI devices that depend on GSIs or IOMMUs are configured.

### Risks
Initialization order is important: GSI mapping must exist before IRQ dependencies and domain lookup are used. RIMT initialization is compile-time gated.

### Test Signals
Boot-test RISC-V ACPI with PLIC, APLIC, SYSMSI, and RIMT combinations; confirm GSI and IOMMU discovery are available before dependent device probing.
