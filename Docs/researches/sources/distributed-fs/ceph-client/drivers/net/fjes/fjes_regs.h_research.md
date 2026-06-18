# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_regs.h

## Purpose
`fjes_regs.h` defines the FJES MMIO register map, register bitfield unions, interrupt masks, and small read/write helper macros used by the hardware layer and ethtool register dumps.

## Important APIs and Types
Register offsets cover information registers (`XSCT_OWNER_EPID`, `XSCT_MAX_EP`), device control (`XSCT_DCTL`), command control (`XSCT_CR`, `XSCT_CS`, command/shared/request/response buffer address registers), and interrupt control (`XSCT_IS`, `XSCT_IMS`, `XSCT_IMC`, `XSCT_IG`, `XSCT_ICTL`). Bitfield unions include `REG_OWNER_EPID`, `REG_MAX_EP`, `REG_DCTL`, `REG_CR`, `REG_CS`, and `REG_ICTL`. Interrupt masks are `REG_ICTL_MASK_INFO_UPDATE`, `DEV_STOP_REQ`, `TXRX_STOP_REQ`, `TXRX_STOP_DONE`, `RX_DATA`, and `ALL`; interrupt status masks include assert and EPID extraction bits. `rd32()` and `wr32()` are convenience accessors around `fjes_hw_rd32()` and `writel()`.

## Control Flow
The header has no standalone execution, but `fjes_hw.c` uses the offsets and unions to reset the device, issue commands, program physical buffer addresses, mask/unmask interrupts, capture status, and generate peer interrupts. `fjes_ethtool.c` uses the same offsets to produce a register dump.

## State, Dependencies, and Integration
It depends on Linux bit operations and forward-declares `struct fjes_hw`. The accessor macros assume a local variable named `hw` with a valid MMIO `base`, so call sites must maintain that convention.

## Risks and Test Signals
Risks are register offset drift against hardware/firmware, C bitfield layout assumptions with `__le32`, accessor macro misuse without a local `hw`, and interrupt mask overlap errors. Tests should validate register dumps, reset bit polling, command request/status decoding, interrupt status EPID extraction, and mask/unmask operations on real or emulated hardware.
