# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_tbl.h

## Purpose
`riva_tbl.h` contains static fixed-function initialization tables for RIVA/NVIDIA hardware blocks. The tables encode register offset/value pairs loaded by `riva_hw.c` during mode setup to initialize PMC, PTIMER, FIFO, PFIFO, PRAMIN, and PGRAPH state for NV3, NV4, and NV10-family chips.

## Important APIs, types, and functions
There are no functions; the API is the table names consumed by `LOAD_FIXED_STATE*` macros in `riva_hw.c`. Important tables include common `RivaTablePMC`, `RivaTablePTIMER`, `RivaTableFIFO`; NV3 `nv3TablePFIFO`, `nv3TablePGRAPH`, `nv3TablePRAMIN` plus 8/15/32 bpp variants; NV4 `nv4TableFIFO/PFIFO/PGRAPH/PRAMIN` plus 8/15/16/32 bpp variants; NV10 equivalents plus `nv10tri05TablePGRAPH` and big-endian conditional values.

## Control flow
No direct control flow exists. Runtime selection happens in `LoadStateExt()`: it writes common tables, then architecture-specific tables, then bpp-specific tables. `UpdateFifoState()` also uses NV4/NV10 FIFO and triangle tables after mode load.

## State and persistence behavior
The arrays are static read-only driver data in practice, although not declared `const`. They become persistent hardware state only when copied into registers. The bpp-specific PRAMIN/PGRAPH tables encode object formats and mono expansion behavior for acceleration.

## Dependencies and integration points
This file is included directly by `riva_hw.c`; table names are coupled to token-pasting macros such as `LOAD_FIXED_STATE(nv10,PGRAPH)`. The values depend on the FIFO object layouts from `riva_hw.h` and the architecture-specific load order in `LoadStateExt()`.

## Risks and test signals
Risks include magic values with little local explanation, mutable static arrays, architecture/bpp table omissions, big-endian conditional coverage, and tight name coupling to macros. Test signals are successful mode load for each supported bpp and architecture, working ROP/fill/blit/image acceleration, and no PGRAPH/PFIFO faults after repeated mode switches.
