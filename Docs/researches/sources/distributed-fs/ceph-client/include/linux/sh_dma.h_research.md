# sources/distributed-fs/ceph-client/include/linux/sh_dma.h

## Purpose

`sh_dma.h` defines platform data and register bit constants for the SuperH dmaengine driver. It bridges platform descriptions of DMA channels and slave request lines to the generic shdma base library and dmaengine API.

## Important APIs, Types, And Functions

`struct sh_dmae_slave` embeds `struct shdma_slave` for platform-provided slave identifiers. `struct sh_dmae_slave_config` maps a `slave_id` to a device address, CHCR value, and MID/RID request selector. `struct sh_dmae_channel` describes channel register offsets and DMARS/CHCLR bit placement. `struct sh_dmae_pdata` aggregates slave arrays, channel arrays, transfer-size field masks and shifts, DMAOR defaults, CHCR interrupt-enable bit, register-width and feature flags, and whether the controller is slave-only.

Constants include DMAOR flags `DMAOR_AE`, `DMAOR_NMIF`, `DMAOR_DME`, address increment/decrement/fixed fields `DM_*` and `SM_*`, request selector values `RS_AUTO` and `RS_ERS`, and channel control flags `CHCR_DE`, `CHCR_TE`, and `CHCR_IE`.

## Control Flow

There is no executable flow. Driver probe reads `sh_dmae_pdata`, configures DMAOR, allocates channels from `channel`, configures slave routes from `slave`, programs transfer-size fields using the shift/mask data, and uses CHCR/DMAOR flags during prepare, start, interrupt, and reset paths.

## State And Persistence

Persistent state is platform data plus hardware register values. Feature bitfields such as `dmaor_is_32bit`, `needs_tend_set`, `no_dmars`, `chclr_present`, `chclr_bitwise`, and `slave_only` determine how implementation code treats each controller throughout its lifetime.

## Dependencies And Integration Points

Dependencies are dmaengine, list handling, `shdma-base.h`, and fixed-width types. Integration points are SuperH/Renesas platform device descriptions, DMA clients using slave IDs, serial SCI DMA paths, and generic dmaengine channel allocation.

## Risks And Test Signals

Risks are wrong slave ID to request-line mapping, invalid transfer-size encoding, mismatched 16/32-bit DMAOR access, incorrect CHCLR reset semantics, and enabling memcpy on slave-only hardware. Test signals include dmaengine memcpy if supported, slave TX/RX for serial or audio clients, channel reset after error, interrupt completion, and platform variants without DMARS or with bitwise CHCLR.
