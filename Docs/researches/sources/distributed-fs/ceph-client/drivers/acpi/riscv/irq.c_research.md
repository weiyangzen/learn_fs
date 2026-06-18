## sources/distributed-fs/ceph-client/drivers/acpi/riscv/irq.c

### Purpose
`riscv/irq.c` implements RISC-V ACPI interrupt-controller ordering, GSI-domain mapping, and automatic ACPI scan dependencies for IRQ providers.

### Important APIs, Types, And Functions
Key APIs include `arch_sort_irqchip_probe()`, `riscv_acpi_update_gsi_range()`, `riscv_acpi_get_gsi_info()`, `riscv_acpi_get_gsi_domain_id()`, `riscv_acpi_init_gsi_mapping()`, and `arch_acpi_add_auto_dep()`. The static `ext_intc_list` holds `struct riscv_ext_intc_list` entries for PLIC, APLIC, and SYSMSI-like controllers.

### Control Flow
MADT IRQ-chip probe entries are sorted by subtype so RINTC precedes IMSIC, APLIC, and PLIC. GSI initialization parses PLIC first and maps `RSCV0001` devices, otherwise parses APLIC and maps `RSCV0002`; SYSMSI devices `RSCV0006` are discovered from namespace `_GSB` because they have no MADT entry. Each external interrupt-controller list entry tracks GSI base, IRQ count, IDC count, ID, ACPI handle, and pending range. Later queries resolve GSIs to ACPI fwnodes. Automatic dependency creation scans `_PRT` or `_CRS` IRQ resources and adds scan dependencies from consumers to IRQ provider handles.

### State, Persistence, And Dependencies
State is the global `ext_intc_list`, allocated during `__init` discovery and retained for runtime lookup. Dependencies include MADT parsing, ACPI namespace device lookup, `_GSB`, `_CRS`, `_PRT`, scan dependency APIs, fwnode conversion, and Linux sort/list helpers.

### Integration Points
Interrupt-controller drivers use GSI info and domain IDs to initialize domains. ACPI scan uses `arch_acpi_add_auto_dep()` to defer consumers until interrupt providers are available.

### Risks
Pending GSI ranges are inferred from the next registered base; ordering and firmware `_GSB` correctness matter. Some allocation failures in dependency creation continue without freeing allocated handle arrays after `acpi_scan_add_dep()` ownership assumptions. `_PRT` entries with missing source handles can add null dependencies if GSI lookup fails. The list insertion loop is subtle because it keeps ranges sorted by descending base.

### Test Signals
Test PLIC-only, APLIC-only, SYSMSI-only, mixed APLIC/SYSMSI, pending range update, `_GSB` missing/failing, GSI lookup boundaries, `_PRT` source and direct-GSI entries, extended IRQ producer filtering, and ACPI scan dependency ordering.
