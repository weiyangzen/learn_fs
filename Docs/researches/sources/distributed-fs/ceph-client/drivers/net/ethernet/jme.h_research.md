# sources/distributed-fs/ceph-client/drivers/net/ethernet/jme.h

## Purpose
`jme.h` is the hardware contract and private driver state definition for the JMicron JMC2x0 Ethernet driver. It defines PCI IDs, ring descriptor formats, MMIO offsets, bit masks, timing constants, cached register defaults, private adapter state, and small inline helpers used by `jme.c`.

## Important APIs, Types, And Definitions
The central types are `struct txdesc`, `struct rxdesc`, `struct jme_buffer_info`, `struct jme_ring`, `struct dynpcc_info`, and `struct jme_adapter`. TX and RX descriptors are 16-byte hardware layouts with separate command, data, and writeback views. `jme_ring` tracks coherent descriptor memory, DMA addresses, per-descriptor buffer metadata, and producer/cleaner indexes. `jme_adapter` ties PCI, netdev, MMIO, MII, rings, locks, tasklets, workqueue, cached registers, revision data, link state, ethtool state, and NAPI together.

Register enums cover MAC, PHY, MISC, and RSS MMIO windows; TX/RX control bits; SMI/MDIO fields; GHC speed/duplex/clock control; PMCS WoL bits; PHY power and link registers; SMB EEPROM interface; timers; interrupt events; packet coalescing; chip mode; and aggressive power mode/pseudo hotplug bits. Inline helpers include `jme_napi_priv()`, `smi_reg_addr()`, `smi_phy_addr()`, `jread32()`, `jwrite32()`, `jwrite32f()`, `is_buggy250()`, and `new_phy_power_ctrl()`.

## Control Flow Support
The header does not execute a standalone control flow; it shapes the implementation in `jme.c`. Descriptor ownership bits define the RX/TX state machine. `INTR_ENABLE` selects the events enabled by `jme_start_irq()`. Default register values such as `RXCS_DEFAULT`, `RXMCS_DEFAULT`, `TXMCS_DEFAULT`, `TXCS_DEFAULT`, and `GPREG*_DEFAULT` seed MAC setup and reset paths. NAPI compatibility macros map the driver's older abstraction layer onto current `struct napi_struct` calls.

## State And Persistence
State persistence is mostly structural: `jme_adapter` caches hardware configuration between operations and across suspend/resume. `reg_pmcs` preserves WoL selection; `old_cmd` preserves ethtool link settings; `flags` records MSI, user speed setting, polling mode, and shutdown state. Descriptor and buffer metadata define ownership transfer between CPU and NIC. Register constants encode hardware persistence points such as EEPROM/SMB contents and PM wake status.

## Dependencies And Integration Points
The header depends on Linux interrupt and networking types brought in by `jme.c`. It is tightly coupled to JMicron hardware register semantics and to the Linux MII, NAPI, DMA, and netdev models. It also includes debug-only register-name tables under `REG_DEBUG`, making MMIO tracing compile-time selectable.

## Risks
Because this file encodes raw hardware layouts, any incorrect bit mask, endianness annotation, descriptor offset, or default value can corrupt DMA or misprogram the MAC. `ETH_CRC_LEN` is defined as 2 in the RX extra length calculation, which is unusual relative to the common 4-byte Ethernet FCS and should be treated as hardware-specific, not generalized. Several enum values share bit positions depending on descriptor context, so code must use the correct descriptor view. The static debug name arrays are only compiled under `REG_DEBUG` but must remain aligned with register spacing if enabled.

## Test Signals
Compilation across relevant kernel configs is the first signal because the header drives many inline and macro call sites. Runtime signals include correct register dumps from ethtool, clean RX/TX descriptor ownership transitions under DMA stress, NAPI scheduling behavior, WoL bit programming, PHY link/speed reporting, and successful operation on chip revisions that trigger `is_buggy250()` and `new_phy_power_ctrl()` branches.
