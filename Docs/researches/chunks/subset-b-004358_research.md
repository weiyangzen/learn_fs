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
