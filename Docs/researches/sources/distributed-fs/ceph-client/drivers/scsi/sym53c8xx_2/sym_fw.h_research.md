<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.h

## Purpose
`sym_fw.h` defines the C interface between the Symbios driver and its SCRIPTS firmware templates. It standardizes label lists, offset-table and bus-address structures, firmware descriptors, firmware declaration macros, script bus-address accessors, and relocation marker encodings used inside the template headers.

## Important APIs, Types, And Functions
Important macros are `SYM_GEN_FW_A`, `SYM_GEN_FW_B`, and `SYM_GEN_FW_Z`, which enumerate externally useful labels in script areas A, B, and Z. Types include `struct sym_fwa_ofs`, `struct sym_fwb_ofs`, `struct sym_fwz_ofs`, their bus-address counterparts `struct sym_fwa_ba`, `struct sym_fwb_ba`, `struct sym_fwz_ba`, and `struct sym_fw`. `SYM_FW_ENTRY()` builds a firmware descriptor from template objects and setup/patch functions. `SCRIPTA_BA()`, `SCRIPTB_BA()`, and `SCRIPTZ_BA()` access computed label bus addresses. Relocation macros include `HADDR_1/2`, `RADDR_1/2`, `SYM_GEN_PADDR_A/B`, and marker constants `RELOC_SOFTC`, `RELOC_LABEL_A`, `RELOC_REGISTER`, `RELOC_LABEL_B`, plus `SCR_DATA_ZERO`.

## Control Flow
There is no runtime control flow. Compile-time macro expansion generates offset structures in `sym_fw.c` and relocation-coded operands in firmware template headers. Runtime code consumes the resulting descriptor and relocation markers in setup/patch/bind functions.

## State And Persistence Behavior
The header defines descriptor shapes and relocation encodings but stores no state. Per-adapter state lives in `struct sym_hcb` fields such as `fwa_bas`, `fwb_bas`, and `fwz_bas`, which match the bus-address structures defined here.

## Dependencies And Integration Points
It depends on `struct sym_hcb`, `struct Scsi_Host`, register offset macro `REG()`, and script struct definitions from firmware headers. It integrates script labels with C code that jumps into script fragments or patches script operands.

## Risks
The key risk is interface drift: adding/removing labels in script templates without updating `SYM_GEN_FW_A/B/Z` or firmware offset structs can break C references or relocation. Relocation marker values must remain consistent with `sym_fw_bind_script()`'s `RELOC_MASK` decoding. `SCR_DATA_ZERO` must not collide with valid script data needing preservation.

## Test Signals
Compile all firmware templates, verify offset-table initialization, run script binding on all firmware areas, inspect `SCRIPTA_BA`/`SCRIPTB_BA` users for valid labels, and test after adding any script label or relocation form.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.h -->
