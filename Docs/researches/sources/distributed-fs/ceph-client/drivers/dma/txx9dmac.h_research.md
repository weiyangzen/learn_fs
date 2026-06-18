# sources/distributed-fs/ceph-client/drivers/dma/txx9dmac.h

## Purpose
`txx9dmac.h` defines the TXx9 DMA controller register layouts, bit definitions, software channel/device/descriptor structures, and compile-time helper functions used by `txx9dmac.c`.

## Important APIs, Types, and Functions
The header defines 64-bit and 32-bit channel register layouts (`struct txx9dmac_cregs`, `struct txx9dmac_cregs32`), controller register layouts (`struct txx9dmac_regs`, `struct txx9dmac_regs32`), and descriptor formats (`struct txx9dmac_hwdesc`, `struct txx9dmac_hwdesc32`). Driver state structures include `struct txx9dmac_chan`, `struct txx9dmac_dev`, and `struct txx9dmac_desc`.

Macros define MCR, CCR, and CSR bits, transfer-size encodings, endian selection (`CCR_LE`, `MCR_LE`), and register padding through `TXX9_DMA_REG32`. Inline helpers include `txx9_dma_have_SMPCHN`, `__is_dmac64`, `is_dmac64`, `txx9dmac_chan_INTENT`, `txx9dmac_chan_set_INTENT`, `txx9dmac_desc_set_INTENT`, `txx9dmac_chan_set_SMPCHN`, and `txx9dmac_desc_set_nosimple`.

## Control Flow and State Model
The header controls driver behavior at compile time. With `CONFIG_MACH_TX49XX`, the driver enables simple-chain support and declares `SMPCHN` available. Without simple-chain support, the descriptor type aliases to the full channel register layout so each descriptor can carry increment and control-register fields. Endianness macros decide whether little-endian mode is programmed in CCR or MCR depending on machine configuration.

`struct txx9dmac_chan` contains its own `dma_device`, tasklet, IRQ, channel CCR template, spinlock, and active/queued/free descriptor lists. `struct txx9dmac_dev` contains MMIO base, optional shared tasklet/IRQ, channel pointers, a 64-bit-register flag, and descriptor size. `struct txx9dmac_desc` deliberately places the hardware descriptor first so the DMA-mapped address points at the exact bytes consumed by hardware, followed by list nodes, child list, dmaengine descriptor, and transfer length.

## Dependencies and Integration Points
The header includes `linux/dmaengine.h` and `asm/txx9/dmac.h`, binding it to TXx9 platform data and `TXX9_DMA_MAX_NR_CHANNELS`. It is private to the driver and not a general kernel API.

## Risks and Review Signals
The main risks are ABI-like layout assumptions: register padding varies by endian and address width, and the hardware descriptor must remain first in `struct txx9dmac_desc`. Compile-time branches create materially different runtime behavior, so both simple-chain and full-descriptor builds need coverage. Review should check that field widths match hardware documentation, that 32-bit and 64-bit `CHAR` handling remains consistent, and that `TXX9_DMA_CCR_XFSZ(__ffs(width))` only sees supported power-of-two widths.
