# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c_hw.h

## Purpose
`atl1c_hw.h` is the hardware register and PHY definition header for `atl1c`. It names MMIO registers, bit masks, field shifts, device IDs, PCIe power controls, DMA/queue controls, interrupt masks, MIB ranges, and PHY debug/MMD registers used by `atl1c_main.c`, `atl1c_hw.c`, and `atl1c_ethtool.c`.

## Important APIs, types, and functions
The only function-like APIs are field helpers `FIELD_GETX`, `FIELD_SETX`, and `FIELDX`, plus prototypes for hardware helper functions implemented in `atl1c_hw.c`. The prototypes cover PHY disable/reset/init, MAC address programming, EEPROM reads, multicast hash programming, MDIO normal/extension/debug access, autoneg restart, power saving, and post-link tuning.

Important register groups include PCI capability and indirect access registers, TWSI/EEPROM/OTP controls, PM/ASPM controls, master reset and interrupt moderation, GPHY control, MDIO controls, MAC control and address registers, WoL controls, SRAM and descriptor base/ring-size registers, TXQ/RXQ/DMA controls, mailbox producer/consumer indices, interrupt status/mask bits, clock gating, and PHY debug/extension registers.

## Control flow and state behavior
This header has no runtime control flow. It defines the hardware state vocabulary that executable code uses for reset sequences, descriptor ring programming, interrupt masking, PHY tuning, EEPROM load, WoL, ASPM, and stats collection. Persistent state may live in EEPROM/OTP or PCI config space; volatile state lives in MMIO registers, PHY registers, and DMA descriptors.

## Dependencies and integration points
It depends on Linux `types.h` and `mii.h`, and on includers providing bit macros. It integrates the driver with Atheros L1C/L2C/L1D hardware revisions and is the authoritative local source for constants consumed by register dump ethtool code, low-level PHY code, probe/reset paths, and TX/RX configuration.

## Risks
Field helper macros are untyped and rely on a strict naming convention where `_MASK` and `_SHIFT` exist. A bad field definition propagates into every read-modify-write call. Some comments document revision-specific behavior, such as L1D v2 timers, L2CB TX FIFO settings, and EEE/AZ registers; applying these generically can cause hardware instability. `IMR_NORMAL_MASK`, `ISR_ERROR`, and `ISR_OVER` define operational interrupt policy, so omissions can hide serious events or produce interrupt storms.

## Test signals
Useful validation includes successful driver compilation, ethtool register dumps matching expected offsets, interrupt delivery and masking under RX/TX load, no DMA hangs after descriptor register programming, correct stats increments from MIB ranges, and stable suspend/resume with ASPM and WoL settings.
