# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004357`: lines 1-5627, `Docs/researches/chunks/subset-b-004357_research.md`
- `subset-b-004358`: lines 5628-7465, `Docs/researches/chunks/subset-b-004358_research.md`

## Chunk Research

### subset-b-004357: lines 1-5627

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

### subset-b-004358: lines 5628-7465

# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2.h lines 5628-7465

## Scope And Purpose

This chunk is the closing section of the Broadcom/QLogic `bnx2` Ethernet driver private header. It covers three broad areas:

- Hardware register constants for the on-chip firmware processors and their queues: TXP, TPAT, RXP, COM, CP, and MCP.
- Driver-facing constants, data structures, and helper macros for ring sizing, NAPI/MSI-X state, RX/TX software descriptors, flash/NVRAM geometry, firmware file layout, and the main `struct bnx2` device state.
- Shared-memory mailbox, link-status, firmware-capability, bootcode-state, remote-PHY, WOL/MBA/VLAN, and iSCSI/host-view offsets used for driver-to-firmware coordination.

The file sits under a `ceph-client` source mirror, but this is a Linux network-driver header, not Ceph filesystem logic. It defines no standalone executable functions except the small inline `get_l2_fhdr()` accessor; most behavior comes from `bnx2.c` and `bnx2_fw.h`, which include this header and use the constants to program PCI/MMIO windows, DMA rings, firmware processors, and shared-memory mailboxes.

The chunk begins immediately after host-coalescing status-block offset helpers and ends at the `#endif` for the header guard.

## Important APIs, Types, And Macros

### Firmware Processor Register Blocks

The repeated `BNX2_<CPU>_*` groups describe the register windows for the embedded processors:

- `BNX2_TXP_*` for the transmit processor at offset `0x40000`.
- `BNX2_TPAT_*` for the transmit patch-up processor at offset `0x80000`.
- `BNX2_RXP_*` for the receive processor at offset `0xc0000`.
- `BNX2_COM_*` for the completion processor at offset `0x100000`.
- `BNX2_CP_*` for the command processor at offset `0x180000`.
- `BNX2_MCP_*` for the management processor at offset `0x140000`.

Each processor block provides CPU mode bits such as local reset, single-step, interrupt enable, soft halt, and bad-access halt enables; CPU state bits such as breakpoint, bad instruction/data address, soft halted, interrupt, stalls, and blocked read; event-mask bits; program counter, instruction, data-access, interrupt, saved-PC, hardware-breakpoint, debug-vector, last-branch, and register-file addresses. Queue definitions such as `BNX2_TXP_TXPQ`, `BNX2_RXP_RXPQ`, `BNX2_COM_COMQ`, `BNX2_CP_CPQ`, and `BNX2_MCP_MCPQ` expose flow-through queue command/control registers with reset, read, add-data, pop, busy, overflow, depth, and intervention bits.

`struct cpu_reg` is the driver abstraction that packages these per-processor addresses. `bnx2_fw.h` instantiates `cpu_reg_com`, `cpu_reg_cp`, `cpu_reg_rxp`, `cpu_reg_tpat`, and `cpu_reg_txp` from this chunk. `bnx2.c` then uses those tables in `load_cpu_fw()` to halt a firmware CPU, clear state, copy text/data/rodata into scratch memory, set the PC, and unhalt it.

### RXP, COM, CP, And MCP Special Registers

RXP adds PFE control, command/completion queues, RX queues, and scratch offsets for RX flooding and RSS table configuration (`BNX2_RXP_SCRATCH_RSS_TBL*`). COM and CP expose checksum-error status, PFE controls, queue windows, scratch bases, and firmware scratch symbols such as `BNX2_FW_RX_LOW_LATENCY`, `BNX2_FW_RX_DROP_COUNT`, and `BNX2_FW_MAX_ISCSI_CONN`.

The MCP block includes management-processor control, attention status, heartbeat, watchdog, access-lock, TOE/function ID, mailbox configuration, MCP/driver doorbells, ROM and scratch bases, chip-specific MCP state addresses, and shared-memory header signature/address fields. These are used by diagnostics and firmware synchronization paths such as `bnx2_dump_mcp_state()`, reset handling, and shared-memory reads/writes.

### PHY, Packet, Ring, And Context Constants

The PHY definitions cover Broadcom 5706/5708/5709 copper and SerDes register layouts: BCM5708S block selection, 1000X control/status, digital and TX/misc blocks, auxiliary controls, DSP/expanded registers, shadow registers, over-1G/BAM/CL73/AER blocks, and speed/duplex/pause bits. Driver link setup and status decoding in `bnx2.c` uses these alongside Linux MII constants.

Packet and ring sizing macros define Ethernet payload bounds, jumbo MTU limit, RX copy threshold, multicast hash count, native-page-limited descriptor page size, descriptor counts, ring masks, and ring-index helpers:

- `BNX2_TX_DESC_CNT`, `BNX2_RX_DESC_CNT`, `BNX2_MAX_*_DESC_CNT`.
- `BNX2_NEXT_TX_BD()` and `BNX2_NEXT_RX_BD()`, which skip the last descriptor slot on a page by advancing by two at the wrap point.
- `BNX2_TX_RING_IDX()`, `BNX2_RX_RING_IDX()`, `BNX2_RX_PG_RING_IDX()`, `BNX2_RX_RING()`, and `BNX2_RX_IDX()`.
- CID and context-address helpers such as `GET_CID_ADDR()`, `GET_CID()`, `GET_PCID_ADDR()`, `MB_GET_CID_ADDR()`, and constants for TX/RX RSS/TSS CIDs.

These macros are part of the driver/firmware ABI for descriptor page layout and context memory addressing. They are used by TX completion, RX refill, NAPI polling, and context initialization in `bnx2.c`.

### Software Descriptor And Device State Types

`struct bnx2_sw_bd`, `struct bnx2_sw_pg`, and `struct bnx2_sw_tx_bd` are the software-side companions for hardware RX/TX descriptors. They store CPU-visible data pointers, pages, SKBs, DMA mappings, GSO state, and fragment counts. `get_l2_fhdr()` derives the L2 firmware header location from an RX data pointer using `PTR_ALIGN(data, BNX2_RX_ALIGN) + NET_SKB_PAD`; `bnx2_alloc_rx_data()`, RX polling, and packet construction use this instead of storing another pointer in each RX software descriptor.

`struct bnx2_tx_ring_info` and `struct bnx2_rx_ring_info` hold producer/consumer indexes, byte-sequence counters, hardware mailbox addresses, descriptor-ring pointers, software-ring pointers, and DMA mappings. `struct bnx2_napi` groups a NAPI object, parent `struct bnx2`, MSI/MSI-X status block pointer, hardware consumer pointers, interrupt number, optional CNIC tag/presence, and one RX/TX ring pair.

`struct bnx2` is the central per-adapter state. It starts with hot-path members (`regview`, `net_device`, `pci_dev`, interrupt semaphore, flags, NAPI/rings, RX buffer sizes, TX constants, optional CNIC state), then stores timer/reset work, PHY and indirect-register locks, PHY state, chip IDs, WOL, firmware sequence/accounting, ring limits, interrupt coalescing values, status/statistics DMA memory, context pages, link configuration and resolved link state, MAC address, shared-memory base, firmware version, PCI capability offsets, flash information, IRQ table, function/ring counts, saved LED state, optional CNIC hooks, and cached firmware handles.

`struct bnx2_irq` describes each interrupt vector handler, vector number, request state, and name. MSI-X limits are fixed at nine hardware/software vectors, with a CNIC build raising the minimum from one to two.

### Flash And Firmware File Layout

Flash constants describe SEEPROM, buffered Atmel flash, Saifun flash, ST Micro flash, and BCM5709 flash page sizes, physical page bits, address masks, and base/total sizes. `struct flash_spec` combines strapping, NVM config words, write command, flags (`BNX2_NV_BUFFERED`, `BNX2_NV_TRANSLATE`, `BNX2_NV_WREN`), page geometry, total size, and a display name. `bnx2.c` uses these in flash/NVRAM detection and read/write/erase paths.

Firmware file structures define the external `request_firmware()` binary layout:

- `struct bnx2_fw_file_section` stores big-endian address, length, and file offset.
- `struct bnx2_mips_fw_file_entry` stores a MIPS CPU start address plus text/data/rodata sections.
- `struct bnx2_rv2p_fw_file_entry` stores an RV2P section plus eight fixup locations.
- `struct bnx2_mips_fw_file` groups COM, CP, RXP, TPAT, and TXP entries.
- `struct bnx2_rv2p_fw_file` groups RV2P processor 1 and 2 entries.

`bnx2_request_uncached_firmware()` validates these structures with section size, offset, alignment, and non-empty checks. `load_rv2p_fw()` applies the `RV2P_P1_FIXUP_PAGE_SIZE_IDX` page-size fixup using `RV2P_BD_PAGE_SIZE`; `bnx2_init_cpus()` loads both RV2P processors and the five MIPS processors.

### MMIO And Shared-Memory Helpers

`BNX2_RD()`, `BNX2_WR()`, and `BNX2_WR16()` are the direct MMIO access macros over `bp->regview`. Indirect helpers in `bnx2.c` build on these for register-window and shared-memory access.

The shared-memory section defines the firmware-driver mailbox ABI:

- Driver reset signature and magic at `BNX2_DRV_RESET_SIGNATURE`.
- Driver mailbox `BNX2_DRV_MB`, message code/data/sequence masks, reset/unload/shutdown/suspend/WOL/diagnostic/pulse/keep-VLAN/set-link message codes, and wait-state encodings.
- Firmware mailbox `BNX2_FW_MB`, acknowledgement mask, and OK/failure status bits.
- Link-status word encodings for link up/down, speed/duplex, autoneg, parallel detect, partner advertisements, TX/RX flow control, SerDes, and heartbeat expiration.
- Driver pulse mailbox and pulse period/firmware acknowledgement timeout values.
- Link command argument bits for speed, autoneg, remote PHY, pause, wirespeed, and PHY reset.

`bnx2_fw_sync()` increments the driver sequence, writes `BNX2_DRV_MB`, waits up to `BNX2_FW_ACK_TIME_OUT_MS` for `BNX2_FW_MB` to echo the sequence, reports `BNX2_DRV_MSG_CODE_FW_TIMEOUT` on timeout, and checks the firmware status field. Reset, suspend, unload, link changes, VLAN-retention updates, diagnostics, and periodic pulse behavior all depend on this ABI.

### Bootcode, Feature, WOL/MBA, Remote PHY, And iSCSI Shared Memory

The later shared-memory offsets describe device/port configuration read from bootcode/NVM: device-info signature and feature validity, part number, power-state masks, hardware config, LED mode, NVM size, bootcode revision, port MAC addresses, default link policy, iSCSI MACs, format revision, feature mask, WOL/MBA/ASF/IMD enablement, BAR1 size, WOL defaults and link speeds, MBA boot-agent/link/option-ROM/BIOS-bootstrap fields, IMD link override, MBA VLAN tag/enable, and MFW version pointer.

Bootcode state fields record reset type, runtime state, errors, management-firmware condition, power-management state, debug command, firmware event code, driver/firmware capability exchange, remote-PHY load/signature/link defaults, iSCSI initiator enablement, maximum iSCSI connection count, and `HOST_VIEW_SHMEM_BASE`. `DP_SHMEM_LINE()` is a diagnostic macro that logs four consecutive shared-memory words via `bnx2_shmem_rd()`.

`BNX2_FW_CAP_CAN_KEEP_VLAN` feeds the driver's `BNX2_FLAG_CAN_KEEP_VLAN`; remote-PHY fields are read when `BNX2_PHY_FLAG_REMOTE_PHY_CAP` is set; iSCSI fields integrate with the optional CNIC path.

## Control Flow And Runtime Behavior

This header mostly provides constants and structs. Runtime control flow appears in consumers:

1. Probe/setup fills `struct bnx2`, maps `regview`, detects chip/PHY/flash capabilities, requests firmware, allocates status/statistics/context/ring memory, initializes NAPI and IRQ vectors, and sets ring counts and coalescing values.
2. Firmware load uses `struct bnx2_mips_fw_file`, `struct bnx2_rv2p_fw_file`, `struct cpu_reg`, and the processor register definitions to load RV2P and MIPS firmware into scratch/register windows and start each embedded CPU.
3. Reset and firmware synchronization use shared-memory mailboxes. The driver writes reset signatures and message codes, waits for firmware acknowledgement, dumps MCP/shared-memory state on timeout, and branches on firmware capability bits.
4. Link management reads PHY registers, shared-memory defaults, and remote-PHY words, then reports link state back to firmware with the `BNX2_LINK_STATUS_*` encoding.
5. RX/TX data paths use `struct bnx2_napi`, ring-info structs, software descriptors, descriptor-count macros, and index helpers to process completions, recycle RX buffers/pages, build SKBs, and advance hardware producer/consumer state.
6. Suspend, resume, unload, WOL, keep-VLAN, diagnostics, and CNIC/iSCSI paths reuse the same shared-memory, firmware, IRQ, and ring state rather than having independent transport mechanisms.

## State And Persistence Behavior

Most state described here lives either in hardware registers, DMA memory, firmware scratch/shared memory, NVM/flash, or `struct bnx2`:

- Hardware processor and queue registers persist until reset, firmware reload, or explicit reprogramming.
- Firmware scratch/shared-memory words persist across driver operations and coordinate bootcode, management firmware, and the host driver; reset paths deliberately write signatures and message codes that firmware observes.
- DMA descriptor rings, status blocks, statistics blocks, context pages, and software descriptor arrays are allocated by the driver and persist while the netdev is open or prepared for operation.
- Firmware blobs are cached in `bp->mips_firmware` and `bp->rv2p_firmware` after successful request/validation and are released during device teardown.
- Link, PHY, flow-control, WOL, ring-count, interrupt-mode, and firmware-sequence state is held in `struct bnx2` and updated by probe, open/close, timer, interrupt/NAPI, ethtool, reset, and power-management paths.
- Flash/NVRAM geometry in `struct flash_spec` is static metadata selected at runtime; actual flash content persists on the adapter and must be modified only through the NVRAM command sequencing in `bnx2.c`.

The header does not encode access semantics for each register bit. Some fields are configuration bits, some are status bits, some are sticky diagnostics, and some are command or self-clearing bits. Consumers must preserve reserved fields, obey firmware handshakes, and respect DMA ownership transitions.

## Dependencies And Integration Points

Primary in-tree consumers are:

- `drivers/net/ethernet/broadcom/bnx2.c`, which uses nearly all device state, MMIO, firmware, ring, flash, PHY, mailbox, WOL, link, and interrupt definitions in this chunk.
- `drivers/net/ethernet/broadcom/bnx2_fw.h`, which maps this chunk's CPU register constants into `struct cpu_reg` tables for firmware loading.
- `drivers/net/ethernet/broadcom/cnic.c` and `cnic.h` when `CONFIG_CNIC` is enabled, using `struct bnx2`, CNIC hooks, status/ring context, and iSCSI-related shared state.

External kernel dependencies include PCI, netdev, NAPI, SKB, DMA mapping, firmware loader, MII/ethtool, timers/workqueues, spinlocks/mutexes, MSI/MSI-X IRQ handling, memory barriers implied by MMIO accessors, and Broadcom/QLogic firmware files declared in `bnx2.c`.

The driver/firmware ABI is especially important. Message-code values, sequence masks, link-status encodings, context/CID address calculations, descriptor page sizing, firmware section layout, RV2P fixup format, and bootcode shared-memory offsets must match the firmware image and the adapter generation.

## Risks And Edge Cases

- Register and mailbox constants are hardware ABI. A wrong offset or bit can halt the wrong firmware CPU, load firmware into the wrong scratch region, corrupt a queue, miss an interrupt, or break reset synchronization.
- The descriptor ring helpers intentionally skip a descriptor at page boundaries. Changing `BNX2_PAGE_BITS`, descriptor sizes, or `BNX2_NEXT_*_BD()` behavior can create producer/consumer mismatches with firmware.
- `get_l2_fhdr()` depends on RX buffer alignment, `BNX2_RX_ALIGN`, and `NET_SKB_PAD`; an allocation/alignment change can make RX header parsing or `build_skb()` offsets wrong.
- Firmware validation is strict about section offsets, length, and alignment. Corrupt or mismatched firmware files fail probe/open; subtly wrong but aligned firmware layout could still load bad code.
- `bnx2_fw_sync()` relies on a 16-bit mailbox sequence and fixed timeout. Lost firmware acknowledgements or stale shared-memory values lead to reset timeouts and MCP state dumps.
- Shared-memory link-status and capability fields cross ownership boundaries among driver, bootcode, management firmware, and remote PHY support. Misinterpreting ownership can cause link flaps, incorrect WOL behavior, VLAN loss, or remote-PHY misconfiguration.
- Flash geometry and NVRAM strapping constants gate persistent writes. Wrong page size, address mask, or write-enable handling risks corrupting adapter NVM.
- MSI-X vector counts are tied to ring and CNIC support. Incorrect `BNX2_MAX_MSIX_VEC`, minimum-vector assumptions, or IRQ-table state can break multi-queue operation or optional CNIC/iSCSI paths.
- The chunk contains legacy-looking compatibility definitions that are not used by the current `bnx2.c` path, including `BNX2_SHARED_HW_CFG POWER_CONSUMED` with an embedded space and several `BNX2_BC_STATE_RESET_TYPE_DRV_*` definitions that reference unprefixed `DRV_MSG_CODE*` names. If new code starts using these names, they should be audited first.
- Hardware status/debug bits such as CPU halted states, queue overflow/intervention, checksum-error status, MCP watchdog/heartbeat, bootcode errors, and iSCSI limits may be read-only or sticky. Treating them as ordinary writable control bits can hide real firmware faults.

## Test Signals

Useful validation signals for this chunk include:

- Build the `bnx2` driver with and without `CONFIG_CNIC` to catch struct, macro, and conditional-field regressions.
- Probe supported BCM5706/5708/5709/5716 adapters and confirm firmware files load, MIPS/RV2P section validation passes, and no firmware sync timeout occurs during reset/open.
- Exercise open/close, reset, suspend/resume, WOL suspend, unload with link down, diagnostics, keep-VLAN update, and link set commands while checking `bnx2_fw_sync()` acknowledgements and MCP state logs.
- Run RX/TX traffic at normal MTU and jumbo MTU, with GSO/TSO, VLAN, checksum offload, and multi-queue/MSI-X enabled, watching for descriptor leaks, DMA mapping errors, TX timeouts, RX drops, and NAPI stalls.
- Test link negotiation across copper and SerDes variants, including 10/100/1000/2500 speeds, forced mode, autoneg, pause negotiation, parallel detect, remote PHY, and heartbeat-expired cases.
- Validate ethtool/NVRAM operations against adapters with different flash parts, especially page-boundary writes and erase/program sequencing.
- Check optional CNIC/iSCSI operation where available: required MSI-X vectors, status block sharing, iSCSI initiator enablement, maximum connection reporting, and CNIC start/stop during netdev state changes.
- Inspect diagnostics for firmware CPU state, queue overflow/intervention, MCP heartbeat/watchdog, bootcode state, firmware capability signatures, and shared-memory lines emitted by `DP_SHMEM_LINE()`.

## Cross-Chunk Notes

The first few lines in this chunk finish host-coalescing status-block offset helpers that were defined in the previous chunk. The final per-file report should merge this with earlier `bnx2.h` chunks before describing the complete register map, descriptor definitions, and driver-private ABI.
