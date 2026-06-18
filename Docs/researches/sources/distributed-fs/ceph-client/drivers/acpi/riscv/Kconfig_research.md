## sources/distributed-fs/ceph-client/drivers/acpi/riscv/Kconfig

### Purpose
`riscv/Kconfig` declares RISC-V-specific ACPI configuration for this directory.

### Important APIs, Types, And Functions
It defines the boolean symbol `ACPI_RIMT`, which controls compilation of RISC-V IOMMU Mapping Table support.

### Control Flow
There is no runtime control flow. Kconfig selection elsewhere enables or disables `CONFIG_ACPI_RIMT`, and the Makefile uses that symbol to include `rimt.o`.

### State, Persistence, And Dependencies
The only state is build configuration. It depends on the surrounding kernel Kconfig system and the RISC-V ACPI build.

### Integration Points
`CONFIG_ACPI_RIMT` gates `drivers/acpi/riscv/rimt.c` and the `riscv_acpi_rimt_init()` call path in `init.c`.

### Risks
The symbol has no prompt in this file, so it must be selected by other configuration logic. If not selected on systems needing RIMT IOMMU discovery, device IOMMU configuration through RIMT will be unavailable.

### Test Signals
Validate build configs with `ACPI_RIMT=y` and unset, confirm `rimt.o` inclusion/exclusion, and boot-test RISC-V ACPI systems with and without RIMT tables.
