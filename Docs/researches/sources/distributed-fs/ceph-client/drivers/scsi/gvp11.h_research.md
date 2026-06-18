# sources/distributed-fs/ceph-client/drivers/scsi/gvp11.h

## Purpose

`gvp11.h` defines register layout, queue defaults, DMA mask, and control-bit constants for the GVP Series II Amiga SCSI controller.

## Important APIs, types, and data

- `CMD_PER_LUN` and `CAN_QUEUE` default to 2 and 16 if not already defined.
- `GVP11_XFER_MASK` describes address bits that prevent direct DMA.
- `struct gvp11_scsiregs` maps padded hardware registers: CNTR, WD33C93 SASR/SCMD, BANK, ACR, start/stop DMA, and undocumented secret registers.
- CNTR bits define DMA busy, interrupt pending, interrupt enable, and write direction.

## Control flow

The header is consumed by `gvp11.c`, which writes the secret registers during probe, uses SASR/SCMD for WD33C93 core access, programs `ACR` and `BANK` for DMA, and toggles `ST_DMA`/`SP_DMA`.

## State and persistence behavior

The structure maps volatile hardware state in Zorro memory space. No software state is allocated here.

## Dependencies and integration points

It depends on Linux fixed-width types and the Amiga/Zorro memory mapping performed by the driver.

## Risks and edge cases

- Register padding is hardware ABI; any layout change breaks MMIO access.
- The include guard lacks a `#define GVP11_H`, so repeated inclusion in one translation unit would not be prevented.
- Secret registers are documented only by comments and driver behavior.

## Test signals

Compile tests can catch the include-guard issue only if the header is included twice with conflicting definitions. Hardware probe and DMA tests validate the register layout.
