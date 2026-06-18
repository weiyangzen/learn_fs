# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/common.h

## Purpose
`common.h` is a central STMMAC header defining core versions, descriptor sizing, statistics structures, feature flags, hardware capability fields, common register bits, flow-control constants, queue/status enums, DMA features, MAC device abstraction, and prototypes shared across STMMAC core files.

## Important APIs, Types, And Functions
- Core version macros identify DWMAC, XGMAC, and XLGMAC revisions.
- Descriptor sizing macros define supported RX/TX descriptor count ranges and defaults.
- `struct stmmac_extra_stats`, `struct stmmac_safety_stats`, queue stats, NAPI stats, and per-CPU stats shape ethtool and runtime accounting.
- `struct dma_features` records decoded hardware feature registers, including checksum, PTP, EEE, queues/channels, RSS, VLAN, TSN, safety, DMA width, and active PHY interface.
- Enums describe packet routing, RX frame status, TX frame status, DMA IRQ status/direction, IRQ request error categories, and FPE events.
- `struct mac_link`, `struct mii_regs`, and `struct mac_device_info` define the hardware abstraction linking MAC, DMA, descriptor, PTP, TC, MMC, EST, VLAN, PCS, MII, link, and filter capabilities.
- Function prototypes expose setup and MAC address helpers used by core implementations.

## Control Flow
This header has no executable control flow except `dwmac_is_xmac()`. It provides constants and type definitions that drive decisions in STMMAC setup, IRQ handling, ethtool stats, queue allocation, feature gating, and platform glue.

## State And Persistence
Types defined here become persistent runtime state in `struct stmmac_priv`, platform data, and hardware abstraction objects. Stats structures persist for the lifetime of the netdev and are exposed through ethtool/netdev APIs.

## Dependencies And Integration Points
It includes Linux netdevice, PHY, XPCS, module, VLAN when enabled, and internal `descs.h`, `hwif.h`, and `mmc.h`. It is consumed by most STMMAC core and glue files, making it a cross-module contract.

## Risks
- Changes to stats structures affect ethtool string ordering and userspace expectations.
- Queue and descriptor size constants must remain powers of two because `STMMAC_NEXT_ENTRY()` uses bit masking.
- `struct dma_features` mirrors hardware feature decoding; incorrect field semantics can enable unsupported offloads.
- Feature flags and enum values are shared across many files, so apparently local edits can have broad effects.

## Test Signals
Build all STMMAC variants, run ethtool stats/selftests where enabled, verify queue count bounds, exercise PTP/EEE/VLAN/TSN feature paths on capable hardware, and check that descriptor sizes are rejected or rounded appropriately by platform configuration.
