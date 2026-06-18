# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_regs.h

- Purpose: Defines the MGB4 register mapping object and basic 32-bit MMIO helpers.
- Important APIs/types/functions: `struct mgb4_regs`, `mgb4_write_reg`, `mgb4_read_reg`, `mgb4_mask_reg`, map/free prototypes.
- Control flow: All MGB4 modules access FPGA registers through this wrapper; mask helper performs read-modify-write.
- State and persistence: State is the mapped MMIO pointer and resource metadata.
- Dependencies and integration points: Depends on Linux `io.h`; integrated across core, CMT, sysfs, vin/vout, trigger, hwmon.
- Risks: Read-modify-write is not internally locked, so callers must serialize shared registers. Macro names evaluate arguments directly.
- Test signals: Compile plus concurrent sysfs/streaming register access tests.
