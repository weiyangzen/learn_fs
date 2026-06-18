<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-ele.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-ele.c

## Purpose
Provides read-only NVMEM access to i.MX93/i.MX94/i.MX95 OCOTP fusebox regions where some words are readable through FSB, some belong to ELE, and some have ECC-width quirks.

## Important APIs, Types, And Functions
`enum fuse_type`, `struct ocotp_map_entry`, and `struct ocotp_devtype_data` describe readable, ELE-owned, ECC, and invalid word ranges. `imx_ocotp_fuse_type()` classifies words. `imx_ocotp_reg_read()` reads valid words, zeros invalid/ELE ranges, masks ECC words to 16 bits, and handles unaligned byte ranges through a temporary buffer. `imx_ocotp_fixup_dt_cell_info()` aligns DT cells to 32-bit raw reads and installs `imx_ocotp_cell_pp()` for MAC byte reversal.

## Control Flow
Probe obtains match data, maps the base, configures a read-only `ELE-OCOTP` NVMEM provider with fixed OF cells, and initializes a mutex. Reads clamp to device size, round to word reads, lock the provider, classify each word, read from `reg_off + index * 4` or synthesize zero, then copy the requested byte slice.

## State And Persistence
State is the SoC map, MMIO base, config, and mutex. Fuse values persist in hardware; ELE-owned or invalid ranges are intentionally hidden as zero.

## Dependencies And Integration Points
Depends on i.MX platform devices, OF match data, MMIO access, NVMEM core fixed cells, and Ethernet MAC post-processing conventions shared with other i.MX OCOTP drivers.

## Risks
Range maps must exactly match SoC fuse ownership; exposing ELE-only words or masking the wrong ECC words would return misleading data. The read-only zero-fill policy can make invalid ranges indistinguishable from programmed zero. Static maps require updates for new SoC revisions.

## Test Signals
Read cells across FSB, ELE, ECC, and invalid boundaries on each supported SoC; verify MAC-address post-processing; confirm out-of-range reads clamp cleanly; and compare reported values with firmware tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-ele.c -->
