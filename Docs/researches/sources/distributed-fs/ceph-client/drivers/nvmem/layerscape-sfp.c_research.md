<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layerscape-sfp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layerscape-sfp.c

## Purpose
Exposes the OTP region of NXP/Freescale Layerscape Security Fuse Processor blocks as a read-only NVMEM provider.

## Important APIs, Types, And Functions
`struct layerscape_sfp_data` supplies OTP size and register endian format per SoC. `layerscape_sfp_read()` bulk-reads 32-bit words from `LAYERSCAPE_SFP_OTP_OFFSET + offset`. Probe creates an MMIO regmap with SoC endian, sets size, and registers `fsl-sfp`.

## Control Flow
OF match selects `ls1021a` big-endian or `ls1028a` little-endian data. Probe maps registers, initializes regmap bounds to the OTP window, and registers a 32-bit aligned NVMEM device. Reads are direct regmap bulk reads.

## State And Persistence
State is just the regmap. Fuse data persists in SFP hardware and this provider is read-only.

## Dependencies And Integration Points
Depends on platform MMIO, device property match data, regmap endian support, and NVMEM core. Cells expose values such as unique IDs and secure boot information.

## Risks
Wrong endian match data produces byte-swapped fuse values. Bulk read count assumes 32-bit aligned accesses enforced by word size and stride. Size constants must match SoC OTP windows.

## Test Signals
Probe both compatible strings, verify endian-correct known fuse words, test unaligned read rejection by the core, and compare provider size with SFP documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layerscape-sfp.c -->
