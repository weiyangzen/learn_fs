# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_csr.h

## Purpose

`fbnic_csr.h` is the central hardware contract for the Meta FBNIC Ethernet driver. It defines descriptor bit layouts, BAR0/BAR4 CSR register indices, queue register geometry, mailbox descriptor format, firmware version gates, interrupt constants, statistics counter addresses, TCAM/RSS table layouts, MAC/PCS/PTP/RXB/RPC/PUL register fields, and the exported register self-test enum/prototype. It has no executable control flow, but almost every runtime file depends on these constants to build descriptors, program hardware, decode debug output, collect stats, test interrupts, and communicate with firmware.

## Important APIs, Types, And Functions

Important macro families include `CSR_BIT()`, `CSR_GENMASK()`, `DESC_BIT()`, `DESC_GENMASK()`, and `FW_VER_CODE()`. Firmware compatibility gates are `MIN_FW_VER_CODE`, `MIN_FW_VER_CODE_LOG`, and `MIN_FW_VER_CODE_HIST`; they are used by firmware bringup and log enablement to reject unsupported firmware or avoid known mailbox flooding behavior. Descriptor definitions cover Tx work descriptors (`FBNIC_TWD_*`), Tx completion descriptors (`FBNIC_TCD_*`), Rx buffer descriptors (`FBNIC_BD_*`), and Rx completion descriptors (`FBNIC_RCD_*`).

Register sections are bracketed by `FBNIC_CSR_START_*` and `FBNIC_CSR_END_*` delimiters. They cover global interrupt registers, per-completion interrupt coalescing, global QM Tx/Rx registers, TCE/TMI/PTP/RXB/RPC/RPC RAM/FAB/Master/PCS/RSFEC/MAC/SIG/MAC_STAT/PUL registers, and per-queue register windows. `FBNIC_QUEUE(n)` plus `FBNIC_QUEUE_STRIDE` define the per-queue CSR window used by Tx/Rx setup, debugfs, stats, and interrupt moderation. BAR4 mailbox constants include `FBNIC_IPC_MBX_DESC_LEN`, `FBNIC_IPC_MBX()`, `FBNIC_IPC_MBX_DESC_*`, and mailbox direction indices.

The only declared function is `fbnic_csr_regs_test(struct fbnic_dev *fbd)`, returning `enum fbnic_reg_self_test_codes`. Other register dump helpers (`fbnic_csr_get_regs()` and `fbnic_csr_regs_len()`) are declared in `fbnic.h`, but use the register map from this header.

## Control Flow

There is no runtime control flow in this header. Its constants drive control flow elsewhere. `fbnic_debugfs.c` uses descriptor masks to render live Tx/Rx rings and mailbox descriptors. `fbnic_fw.c` uses mailbox register offsets and descriptor bits to initialize, publish, poll, and recycle DMA mailbox pages. `fbnic_irq.c` uses interrupt masks, vectors, and MSI-X control registers to request mailbox/MAC/NAPI interrupts and exercise the MSI-X self-test. `fbnic_hw_stats.c` uses TCE/TMI/RXB/RPC/PUL/MAC/PCS register addresses to reset and accumulate hardware counters. `fbnic_ethtool.c` uses queue/coalescing/RSS/TCAM limits and masks to validate user input and expose stats.

## State And Persistence

The file itself stores no state. It defines how state is represented in device registers and descriptors. Persistent driver behavior depends on these definitions remaining aligned with firmware and silicon: queue head/tail state, DMA addresses, descriptor ownership bits, mailbox completion bits, TCAM entries, RSS key/table storage, hardware stats, interrupt masks, and firmware version encodings are all interpreted through these masks.

## Dependencies And Integration Points

The header depends on Linux bit helpers and `FIELD_PREP/FIELD_GET` users in including files. It is included directly or indirectly by nearly all FBNIC modules through `fbnic.h` and more targeted headers. Integration points include Linux netdev Tx/Rx descriptor handling, ethtool register dump/self-test paths, firmware mailbox TLVs, devlink firmware flash/coredump health paths, debugfs visibility, and hardware monitor sensor reads through MAC-specific helpers.

## Risks And Edge Cases

Register or bitfield drift is the primary risk: a wrong mask silently corrupts descriptors or programs the wrong hardware register. Queue register formulas must stay in CSR-index units rather than byte offsets; call sites add these indices to `u32 __iomem *` BAR pointers. The page-size-dependent Rx buffer fragment macros are subtle because they encode both page address and fragment ID behavior for systems with pages larger than 4 KiB. Firmware version constants gate safety-sensitive features; lowering them can expose unsupported firmware paths, while raising them can reject otherwise usable devices. The mailbox descriptor length and address masks must remain consistent with firmware's DMA interpretation.

## Test Signals

Useful validation includes register self-test success, ethtool register dump size/version sanity, MSI-X self-test pass, successful mailbox bringup across reset, debugfs descriptor decode matching live queue movement, hardware stats increasing without obvious wrap artifacts, RSS key/table programming tests, and firmware log gating on versions below and above the documented thresholds. No executable tests were run for this research item.
