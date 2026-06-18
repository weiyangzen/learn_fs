# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_riscv.c

## Purpose
Implements the RISC-V firmware-processor backend: wrapper remap programming, ELF firmware processing, coremem boot-data patching, firmware heap setup, VM mapping, firmware address conversion, and IRQ handling.

## Important APIs, types, and functions
- `pvr_riscv_wrapper_init()` programs FWCORE bootloader code/data remap windows from firmware object GPU addresses.
- `struct rogue_riscv_fw_boot_data` describes boot-data fields patched at the start of FW data memory.
- `pvr_riscv_fw_process()` loads ELF PT_LOAD segments and patches optional coremem code/data addresses and sizes.
- `pvr_riscv_init()` initializes a 32 MiB firmware heap.
- `pvr_riscv_get_fw_addr_with_offset()`, `pvr_riscv_vm_map()`, `pvr_riscv_vm_unmap()`, `pvr_riscv_irq_pending()`, and `pvr_riscv_irq_clear()` complete `pvr_fw_defs_riscv`.

## Control flow
Firmware processing is straightforward: common ELF processing populates code/data/core allocations, then boot data at the start of data memory is filled with GPU virtual addresses, FW addresses, and object sizes for coremem sections if they exist. Wrapper init builds common remap options from heap size and FW private MMU context, asserts address alignment, writes bootloader code and data remap registers, and sets Garten idle control before common start code releases the FW core and toggles `ROGUE_CR_FWCORE_BOOT`.

## State and persistence
No extra processor-private state is allocated. RISC-V persistent state is the common firmware heap, FW objects, and boot-data fields. Firmware address cacheability is encoded by ORing either shared uncached or shared cached region bases into the FW address.

## Dependencies and integration points
Depends on Rogue RISC-V register/region macros, common ELF processing, kernel VM mapping, FW object GPU/FW address helpers, and common start/stop code. Selected by the common firmware vtable for RISC-V processor type.

## Risks
Remap register programming assumes FW object GPU addresses satisfy hardware alignment. The boot-data struct is local to this file and must stay ABI-compatible with firmware. Cacheability is address-region based, so incorrect object flags translate into wrong FW-visible regions.

## Test signals
Validate RISC-V firmware boot with and without coremem sections, remap alignment WARNs, IRQ pending/clear behavior, boot-data contents, and correct behavior for cached versus uncached FW objects.
