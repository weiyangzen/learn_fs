## sources/distributed-fs/ceph-client/drivers/acpi/riscv/rhct.c

### Purpose
`riscv/rhct.c` reads the RISC-V Hart Capabilities Table to expose per-CPU ISA strings and cache-block operation sizes.

### Important APIs, Types, And Functions
The exported-style functions are `acpi_get_riscv_isa()` and `acpi_get_cbo_block_size()`. `acpi_get_rhct()` caches the RHCT table for runtime use, and `acpi_parse_hart_info_cmo_node()` extracts CMO node data referenced by hart-info nodes.

### Control Flow
`acpi_get_riscv_isa()` maps a Linux CPU to an ACPI CPU UID, obtains either a caller-provided RHCT table or the cached runtime table, scans RHCT nodes for a hart-info node with a matching UID, follows its node offsets, and returns the first referenced ISA string node. `acpi_get_cbo_block_size()` resets requested outputs to zero, scans all hart-info nodes, follows CMO references, and records `BIT(encoded_size)` for CBOM, CBOZ, and CBOP sizes while warning if sizes differ across harts.

### State, Persistence, And Dependencies
The cached RHCT pointer is retained without releasing the ACPI table mapping because runtime callers may reuse it. Dependencies include ACPI table APIs, RHCT struct definitions, ACPI CPU UID lookup, and bit helpers.

### Integration Points
RISC-V architecture code can query ISA strings and CBO block sizes during early boot or runtime. Callers that already own an RHCT mapping can pass it in and release it themselves later.

### Risks
The parser trusts RHCT node lengths and offsets from firmware. Encoded CBO sizes above 30 are ignored. ISA lookup returns `-1` rather than a conventional errno when no matching node is found. Cached-table lifetime follows ACPI core behavior.

### Test Signals
Test absent RHCT, caller-provided table, matching and missing CPU UIDs, multiple ISA references, malformed offsets, consistent and inconsistent CBO sizes, encoded sizes above 30, and ACPI-disabled paths.
