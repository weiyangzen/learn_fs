<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_riscv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_riscv.h

Purpose: Defines the Rogue RISC-V firmware region map and helper macros for region base addresses and remap control registers.

Important APIs/types/functions: `enum rogue_riscvfw_region` assigns 256 MiB region indexes for SOCIF, bootloader data/code, shared cached/uncached data, and core memory. `ROGUE_RISCVFW_REGION_BASE(r)` computes a firmware-visible region base; `ROGUE_RISCVFW_REGION_REMAP_CR(r)` computes the corresponding firmware-core remap register offset.

Control flow: No runtime flow; it is a low-level address/remap definition header.

State and persistence behavior: The constants define persistent firmware address layout and the control registers used to program remaps for the RISC-V firmware processor.

Dependencies: Includes `pvr_rogue_cr_defs.h` for `ROGUE_CR_FWCORE_ADDR_REMAP_CONFIG0`, plus Linux bitops, sizes, and types.

Integration points: Used by RISC-V firmware initialization/remap code in the same PowerVR driver family. It complements the MIPS-specific firmware address definitions.

Risks: Region index drift changes all derived bases and remap registers. This can make firmware boot from the wrong region or map shared data incorrectly.

Test signals: Successful RISC-V firmware load/start, correct remap register programming, firmware trace/shared-memory access, and build coverage for all region macro users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_riscv.h -->
