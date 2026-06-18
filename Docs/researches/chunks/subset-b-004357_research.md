# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2.h lines 1-5627

## Scope

This chunk covers the first 5,627 lines of `bnx2.h`, the generated hardware ABI header for the QLogic/Broadcom `bnx2` Ethernet driver. The covered range contains the wire/DMA structures and most of the register map used by `bnx2.c` for descriptor rings, interrupt status blocks, statistics DMA, PCI/GRC access, reset and clock control, NVM/flash transactions, context memory, EMAC/MDIO, RX parser/filtering, RSS, receive buffers, RV2P firmware engines, mailbox queues, TX BD fetch/cache/DMA, and the beginning of host coalescing/MSI-X status block configuration.

## Purpose

`bnx2.h` is not an algorithmic module; it is the device contract. It gives the C driver exact structure layouts, register offsets, bit masks, register-window constants, queue addresses, and helper value macros that must match the NIC firmware and silicon. The driver includes it so MMIO reads/writes, DMA descriptor contents, status block interpretation, and firmware-visible context memory all use the same ABI as the Broadcom/QLogic hardware.

The top comment explicitly says the hardware data structures and register definitions are generated from RTL and should not be modified. That is important: many names are awkward, duplicated, or revision-qualified (`_XI`, `_TE`) because they mirror hardware revisions rather than a hand-designed software API.

## Important Types and ABI Layouts

- `struct bnx2_tx_bd`: transmit buffer descriptor written by the driver into TX rings. It contains a 64-bit host address split into high/low words, an MSS/byte-count field, and VLAN/flag bits. Important flags include checksum offload (`TX_BD_FLAGS_TCP_UDP_CKSUM`, `TX_BD_FLAGS_IP_CKSUM`), VLAN tagging, coalescing now, start/end markers, and software LSO/SNAP hints.
- `struct bnx2_rx_bd`: receive buffer descriptor written by the driver into RX rings. It contains a 64-bit DMA buffer address, buffer length, and simple start/end/dummy/nopush flags. `BNX2_RX_ALIGN` is 16, reflecting hardware alignment requirements.
- `struct status_block`: legacy/MSI status block DMA layout. It exposes attention bits, acknowledge bits, per-ring quick consumer indexes, completion/cmd indexes, status index, and status block number. The field order is conditional on `__BIG_ENDIAN` versus `__LITTLE_ENDIAN`, so the memory image matches what the hardware writes.
- `struct status_block_msix`: compact MSI-X status block layout for one vector/ring, aligned by `BNX2_SBLK_MSIX_ALIGN_SIZE` of 128 bytes.
- `struct statistics_block`: DMA statistics area with high/low 64-bit counter pairs and 32-bit counters for Ethernet MIB, pause/flow-control, filter discard, rule checker, catchup, generic firmware stats, and firmware RX drops.
- `struct l2_fhdr`: receive frame header placed before packet data. It carries parse/classification status, RSS hash, packet length, VLAN tag, and IP/TCP/UDP checksum values. `BNX2_RX_OFFSET` is `sizeof(struct l2_fhdr) + 2`, which explains the RX data offset used to align packet payloads after the hardware header.

These structures are consumed directly in `bnx2.c`: memory allocation sizes use `sizeof(struct status_block)` and `sizeof(struct statistics_block)`, RX allocation and refill manipulate `struct bnx2_rx_bd`, TX path fills `struct bnx2_tx_bd`, interrupt handlers read `status_block`/`status_block_msix`, and RX processing reads `struct l2_fhdr`.

## Register Families Covered

- L2 context and BD chain context: `BNX2_L2CTX_*` constants define context-memory offsets for TX host indices, byte sequences, TX BD reader addresses, RX BD chain state, page BD state, jumbo RBDC keying, and status block routing macros (`BNX2_L2CTX_L5_STATUSB_NUM`, `BNX2_L2CTX_L2_STATUSB_NUM`).
- PCI/PCIe configuration: `BNX2_PCICFG_*` and `BNX2_PCI_*` define MSI control, indirect GRC register windows, interrupt acknowledge commands, PCI clock/power/status, VPD, device IDs, MSI/MSI-X tables/PBA, PCIe capability fields, and BAR/window sizing.
- MISC block: `BNX2_MISC_*` covers global enable/disable/status bits for hardware engines, reset/shutdown, clock and PLL control, GPIO/SPIO/PPIO, SMBus/ASF management, parity enable/status, chip identity, NVM write protection, BIST, OTP, dual-media/PHY strap control, and attention/error facilities.
- NVM block: `BNX2_NVM_*` defines flash/SPI command, address, read/write data, configuration opcodes, flash size/vendor, arbitration, and access enable bits. These are used by flash read/write/erase paths and firmware/NVRAM configuration loading.
- DMA block: `BNX2_DMA_*` defines global DMA enable/status/configuration, read/write master settings, arbitration, blackout/retry behavior, tag RAM entries, read/write channel status, and fuse controls.
- Context block: `BNX2_CTX_*` defines context memory command/status, virtual/page-table registers, context data access, locks, 5709 context control/data, host page table programming, CAM operations, cache status, DMA channel status, and checksum/error reporting.
- EMAC block: `BNX2_EMAC_*` defines MAC mode/status/attention, LED behavior, exact-match MAC filters, MTU/jumbo enable, SerDes, MDIO command/status/mode, TX/RX mode, multicast hash registers, RX/TX statistics, and RX/TX MAC debug state registers.
- RPM block: `BNX2_RPM_*` defines RX parser command/config, VLAN matching, per-user sort rules, parser discard counters, IPv6 programmable extension handling, rule checker controls and value/mask pairs, ACPI/wake pattern matching, and extensive parser debug state.
- RLUP/RSS block: `BNX2_RLUP_RSS_*` defines RSS configuration, indirection table command access, hash mask, and RSS data register.
- RBUF block: `BNX2_RBUF_*` defines receive buffer enable/init, free counts, firmware buffer allocation/free/select, and MTU-dependent XON/XOFF/drop/keep threshold macros.
- RV2P block: `BNX2_RV2P_*` defines the embedded processor command/reset/stall controls, instruction load registers, per-processor address commands, generated buffer addresses, and processor/feed/FTQ queues used when loading firmware code.
- MQ/TSCH/TBDR/TBDC/TDMA blocks: these define mailbox queue command and mapping, transmit scheduler TSS config, TX BD reader control and FTQ, TX BD cache CAM/debug controls, and transmit DMA command/config/debug/checksum/FTQ controls.
- HC block through line 5,627: `BNX2_HC_*` defines host coalescing enable/status/config, status/statistics DMA addresses, RX/TX/completion/cmd interrupt trip and tick timers, statistics selector/result registers, coalesce-now/MSI-X vector bits, and repeated per-status-block coalescing register groups for status blocks 1 through 8.

## Control Flow and Data Flow

The normal driver flow is: probe maps BAR/MMIO, initializes chip blocks using these register constants, allocates descriptor/status/statistics DMA memory using the ABI structures, programs hardware with DMA addresses, enables parser/MAC/DMA/host coalescing blocks, then exchanges ring indexes and status updates with hardware.

Transmit flow is represented in this header by `bnx2_tx_bd`, L2 context offsets, TX BD reader/cache (`TBDR`/`TBDC`), TX DMA (`TDMA`), scheduler (`TSCH`), and host coalescing completion indexes. Software fills TX BDs with DMA addresses and offload flags, hardware fetches them through TBDR/TBDC, TDMA reads packet data, and HC/status blocks report consumer progress.

Receive flow is represented by `bnx2_rx_bd`, `l2_fhdr`, EMAC/RPM/RBUF/RLUP registers, and status block RX consumer indexes. Software posts RX buffer descriptors; EMAC receives frames; RPM classifies/filter-checks, strips or preserves VLAN according to RX mode, computes checksum/status fields, and writes the L2 frame header; RLUP can compute RSS; RBUF manages internal buffering and flow-control thresholds; hardware updates status blocks for NAPI polling.

Interrupt flow uses PCI config interrupt acknowledge registers plus HC status block registers. `BNX2_PCICFG_INT_ACK_CMD` masks/unmasks and acknowledges interrupt indexes; `BNX2_HC_*` defines status DMA addresses, coalescing timing, trip thresholds, attention bits, and per-vector/status-block settings. Legacy/MSI uses `struct status_block`; MSI-X uses `struct status_block_msix` with 128-byte spacing.

Management and persistence flow uses MISC/SMBus/ASF and NVM registers. The driver arbitrates for NVM access with `BNX2_NVM_SW_ARB`, enables write permissions through `BNX2_MISC_CFG_NVM_WR_EN_*` and `BNX2_NVM_ACCESS_ENABLE`, then issues command/address/data sequences with `BNX2_NVM_COMMAND`, `BNX2_NVM_ADDR`, `BNX2_NVM_READ`, and `BNX2_NVM_WRITE`.

Firmware/control-processor flow uses RV2P instruction and processor command registers. `bnx2.c` loads firmware words through `BNX2_RV2P_INSTR_HIGH/LOW` and `BNX2_RV2P_PROC{1,2}_ADDR_CMD`, then resets/stalls/enables the RV2P engines using `BNX2_RV2P_COMMAND` and `BNX2_RV2P_CONFIG`.

## State and Persistence Behavior

Most definitions in this chunk describe volatile device state: MMIO registers, hardware queues, DMA-visible status blocks, and descriptor rings. The persistent surface is NVM/flash: `BNX2_NVM_*` and related `BNX2_MISC_CFG_NVM_WR_EN_*` bits control operations that can alter device firmware/configuration. Because the same register window also reads persistent VPD/flash data, correctness of arbitration and write-enable sequencing is critical.

The status and statistics structures are DMA-coherent shared memory, not persistent storage. They are initialized and mapped during device open/probe and then repeatedly updated by the NIC. Endianness-specific layouts mean any change to field order or compiler packing assumptions can break status consumption without a compiler error.

The context block persists only as long as hardware context memory is initialized and powered. `BNX2_CTX_HOST_PAGE_TBL_*`, `BNX2_CTX_COMMAND_MEM_INIT`, and related page table definitions are used to back context memory with host pages on chips that require it.

## Dependencies and Integration Points

- Linux kernel networking stack: the structures feed netdev TX/RX rings, NAPI polling, checksum offload, VLAN handling, RSS, multicast/promiscuous filtering, statistics, and interrupt moderation.
- PCI/MSI/MSI-X subsystem: PCI config, MSI/MSI-X table/PBA addresses, interrupt acknowledge fields, status block alignment, and MSI control bits are all defined here.
- DMA API: descriptor rings, status blocks, statistics blocks, and context pages are allocated as DMA-visible memory in `bnx2.c`; this header defines their exact device-facing shape.
- PHY/MDIO layer: EMAC MDIO command/mode bits are used by PHY read/write functions, including auto-poll disable/restore sequences.
- Firmware blobs and management firmware: RV2P instruction registers, shared memory access via indirect GRC windows, SMBus/ASF controls, link status reporting, and NVM configuration fields coordinate with firmware-side behavior.
- Hardware revision handling: many definitions have base and `_XI` or `_TE` variants. Callers must select the right value based on chip family/revision, not by name similarity.

## Risks and Sharp Edges

- ABI drift: generated register offsets and descriptor layouts must match silicon/firmware. Seemingly harmless renames, type-width changes, packing changes, or endian layout edits can break hardware communication.
- Endianness: `status_block`, `status_block_msix`, and `l2_fhdr` have explicit big/little endian field order. Testing only on little-endian machines can miss big-endian breakage.
- MMIO ordering: many register sequences require read-backs or polling on busy/done bits (`MDIO_COMM_START_BUSY`, `NVM_COMMAND_DONE`, context write requests, TBDC register arbitration). Incorrect ordering can cause timeouts or stale reads.
- Persistent flash writes: NVM write-enable and erase/write commands can modify adapter contents. Tests or debug tools must not issue write/erase paths accidentally.
- Interrupt moderation and status block sizing: MSI-X status blocks assume `BNX2_SBLK_MSIX_ALIGN_SIZE` and per-block HC offsets. Miscomputed sizes or vector indexes can corrupt adjacent DMA state or silence interrupts.
- MTU threshold macros: `BNX2_RBUF_CONFIG*_VAL(mtu)` calculate internal buffer watermarks from MTU. Out-of-range MTUs or formula changes may affect flow control and packet drops under jumbo frames.
- Hardware revision variants: `_XI` bit positions sometimes overlap or redefine older fields. Using non-XI constants on XI chips, or the reverse, can corrupt unrelated control bits.
- Register window access: indirect GRC access through `BNX2_PCICFG_REG_WINDOW_ADDRESS`/`BNX2_PCICFG_REG_WINDOW` is shared infrastructure. Bad offsets or concurrent unprotected accesses can target the wrong hardware block.

## Test and Validation Signals

- Build coverage with `bnx2.c` included should catch missing symbols and some type-width mistakes, but not ABI semantic regressions.
- Probe/open smoke tests should confirm BAR mapping, chip ID readout, context initialization, ring allocation, status/statistics DMA programming, and interrupt enablement.
- Link tests should exercise EMAC mode changes, MDIO PHY reads/writes, link-up/down attention bits, flow-control negotiation, and MAC mode writes.
- TX/RX traffic tests should cover checksum offload, VLAN tag insertion/stripping, LSO, jumbo MTU, multicast filtering, promiscuous mode, RSS distribution, and ring wraparound.
- Interrupt tests should cover INTx/MSI/MSI-X paths, coalescing timers/trips, attention bits, masking/unmasking via `BNX2_PCICFG_INT_ACK_CMD`, and per-vector status index updates.
- NVM tests should prefer read-only paths, verifying arbitration acquisition/release and flash identification/config decoding without write-enable unless on disposable hardware.
- Error-path diagnostics should monitor parity/error/status registers, TBDC/TDMA/TBDR debug state, RBUF free counts, RPM discard counters, and HC visibility registers when stress traffic or fault injection is available.

## Research Notes

The source range is primarily definitions rather than executable code. Substantive behavior comes from how `bnx2.c` consumes these definitions: register read/write helpers use the PCI/GRC windows; PHY helpers use EMAC MDIO bits; NAPI and interrupt handlers consume status block layouts; RX processing consumes `l2_fhdr`; reset/init paths program MISC, DMA, CTX, RBUF, EMAC, RPM, RV2P, TBDR, TDMA, and HC registers; flash helpers consume the NVM register set. The merge lane should treat this chunk as the low-level hardware ABI foundation for the later driver code research.
