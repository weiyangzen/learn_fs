# sources/distributed-fs/ceph-client/drivers/edac/pnd2_edac.h

## Purpose
Defines Pondicherry2 memory-controller register bitfield layouts and access metadata used by `pnd2_edac.c`. It covers top-of-memory PCI registers, slice/channel hash and asymmetric region registers, MOT range registers, and Apollo Lake/Denverton D-unit geometry registers.

## Important APIs, Types, And Functions
- `b_cr_touud_*`, `b_cr_tolud_pci`, and MCHBAR structs describe memory limits and MCHBAR base enablement.
- `b_cr_slice_channel_hash`, asymmetric region structs, and MOT structs describe first-stage interleave and region decode controls.
- `d_cr_drp0` describes Apollo Lake DIMM presence, ECC, address map, bank/rank hash, density, width, and DRAM type.
- `d_cr_dsch`, `d_cr_ecc_ctrl`, `d_cr_drp`, and `d_cr_dmap*` describe Denverton channel, ECC, DIMM rank, and address-bit mapping.
- The `*_port`, `*_offset`, and `*_r_opcode` macros provide register-access metadata consumed by `RD_REG` and `RD_REGP`.

## Control Flow
The header has no executable control flow. Its bitfields are populated by the active `dunit_ops->rd_reg` implementation and then consumed by topology construction, ECC checks, DIMM configuration, and address decoding.

## State And Persistence
No runtime state is stored in the header. Instances of these structures are cached as static globals in `pnd2_edac.c` after probe and treated as stable hardware configuration.

## Dependencies And Integration Points
The structures rely on Linux fixed-width integer types and compiler bitfield layout matching the target little-endian register interpretation. The metadata macros are tightly coupled to the sideband/MMIO/config-space access helpers in `pnd2_edac.c`.

## Risks And Edge Cases
C bitfield layout is compiler and endian sensitive, so this header is appropriate only for the intended kernel/architecture ABI. Register fields differ between Apollo Lake and Denverton, which is why separate structs exist; using the wrong struct or opcode would corrupt decode. Reserved sentinel values such as `31` and `0x3f` in DNV maps must be interpreted carefully by the decoder.

## Test Signals
Compile on the intended x86 configs, compare decoded struct fields against raw register dumps, validate APL and DNV register metadata, and run address-decode tests for every mapped row/column/bank/rank field combination.
