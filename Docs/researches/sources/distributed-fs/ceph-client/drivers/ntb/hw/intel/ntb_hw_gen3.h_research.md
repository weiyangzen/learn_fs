# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen3.h

Purpose: Provides Intel Skylake/Gen3 NTB register offsets, resource counts, inline 64-bit doorbell accessors, and exported Gen3 function prototypes.

Important APIs, types, and functions: Defines Gen3 PCI config offsets for BAR sizes and error/link status, BAR0 MMIO offsets for NTB control, IM/EM BAR xlat/limits, interrupt status/masks, interrupt vectors, SPADs, doorbells, B2B SPADs, and secondary command/BARs. `GEN3_DB_COUNT`, `GEN3_DB_LINK`, vector constants, and `GEN3_SPAD_COUNT` describe resources. `gen3_db_ioread()`/`gen3_db_iowrite()` provide 64-bit DB access wrappers. Externs declare debugfs, init, link, DB, peer DB, and `intel_ntb3_ops`.

Control flow: No direct flow, but the offsets drive Gen3 init, debugfs, interrupts, DB operations, and MW translation in `ntb_hw_gen3.c`.

State and persistence behavior: Hardware state addressed by this header persists in Gen3 MMIO/config registers; runtime state is stored in `intel_ntb_dev` via shared register descriptor structures.

Dependencies and integration points: Includes `ntb_hw_intel.h` and is consumed by the main Gen1 file and Gen3 implementation. The main Intel driver references `intel_ntb3_ops` and `gen3_init_dev()` through this header.

Risks and edge cases: Doorbell register size is represented as `sizeof(u32)` in the Gen3 reg table while accessors read/write 64-bit masks; this matches the logical DB mask implementation but deserves hardware regression coverage. Offsets for IM and EM spaces are separated by `0x4000`; incorrect descriptor selection would target the wrong side.

Test signals: Compile checks, debugfs register sanity on SKX hardware, DB mask/vector tests, and MW xlat/limit register readback tests are the best validation signals.
