# Group Research: group_606_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__8a252a16d203

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is in subset A. All 21 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mii.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mii.h

## Purpose

`nxge_mii.h` defines the NXGE driver's view of standard MII/GMII PHY registers and a small Broadcom-style shadow mode-control register. It is a hardware interface header: it exports register numbers, a compact register-index table, and 16-bit register union layouts with endian-aware bitfield ordering.

## Main Definitions

The register constants cover standard MII registers beyond the common `miiregs.h` set: link-partner next page, gigabit control/status, extended status, a vendor shadow register, and a mode-control shadow register. `NXGE_MAX_MII_REGS` fixes the PHY register index table at 32 slots.

`mii_regs_t` names the MII register indices as byte offsets: BMCR, BMSR, PHY IDs, autoneg advertisement/link partner/expansion/next page, gigabit control/status, extended status, vendor-reserved fields, and shadow registers.

The union definitions map the 16-bit register payloads: BMCR for reset/loopback/speed/autoneg/duplex controls; BMSR for link capabilities and status; ID registers for OUI/model/revision; autoneg registers for advertisement and next-page state; gigabit control/status; extended status; and `mii_mode_control_stat_t` for copper/fiber mode, signal state, energy state, change indication, enable, and write-enable bits.

## Integration Notes

The header depends on `<sys/miiregs.h>` and illumos `_BIT_FIELDS_HTOL` / `_BIT_FIELDS_LTOH` conventions. It has no functions and no storage. Consumers read/write MDIO registers as raw `uint16_t` values and interpret fields through these unions.

## Research Notes

The file is sensitive to hardware bit ordering, not control flow. Potential audit issues are register-layout drift, misuse of shadow-register write-enable semantics, and typo-like formatting in a few bitfield blocks, though the bit widths themselves add up to 16.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mii.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_n2_esr_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_n2_esr_hw.h

## Purpose

`nxge_n2_esr_hw.h` defines MDIO-visible register addresses and bitfields for the N2/NIU embedded SerDes blocks, covering two TI macro families: `WIZ6C2xxN2x0` and `WIZ7c2xxn5x1` / KT NIU. It is used by NXGE SerDes initialization and tuning code to program PLL, transmit, receive, status, and test registers.

## Register Map

The header defines `ESR_N2_DEV_ADDR` as device address `0x1e` and `ESR_N2_BASE` as `0x8000`. Register block offsets separate PLL, test, TX lanes, RX lanes, and a P1 block. Address macros compute low/high 16-bit MDIO words for PLL config/status, test config, and TX/RX config/status for channel `chan`.

The macros use 4-word spacing per TX or RX lane and expose both combined and low/high register names.

## WIZ6C2xxN2x0 Definitions

The first register family defines PLL enable/multiplier/loop bandwidth, RX enable/test/bus width/rate/pair inversion/termination/alignment/LOS/equalization/CDR fields, RX status fields, TX enable/test/bus width/rate/pair inversion/common mode/swing/de-emphasis/BIST fields, and pattern-test loopback controls.

Named constants enumerate PLL multipliers, RX CDR/equalization modes, TX swing/de-emphasis settings, bus widths, rates, terminations, alignment modes, and loopback modes.

## WIZ7 / KT / NIU Definitions

The KT-family definitions add wider PLL multipliers, `divclken`, clock bypass, PLL lock/divclk status, simplified test controls, expanded TX/RX bus-width fields, TX idle/sync/loopback/detect fields, and RX open-circuit/equalizer/loopback controls.

`nxge_serdes_prop_t` is a software property bundle for optional SerDes overrides: TX low/high, RX low/high, PLL low, and a bitmask saying which properties are set. The property bits are `NXGE_SRDS_TXCFGL`, `NXGE_SRDS_TXCFGH`, `NXGE_SRDS_RXCFGL`, `NXGE_SRDS_RXCFGH`, and `NXGE_SRDS_PLLCFGL`.

## Research Notes

This file is a pure ABI map for SerDes programming. The main risk is incorrect lane/channel arithmetic or applying constants from the wrong TI macro family. The `buswwidth` field spelling and `LOOOPBACK` constant spelling are historical API spellings that callers may depend on.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_n2_esr_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_phy_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_phy_hw.h

## Purpose

`nxge_phy_hw.h` is the NXGE external PHY hardware catalog. It defines PHY IDs, MDIO clause types, port-address bases, device/register addresses, bitfield layouts, and small property structures for Broadcom, Marvell, Teranetics, NetLogic/AEL2020, SFP+, and QSFP PHY/module support.

## PHY Identification And Addressing

The header reserves ports 0 through 5 for on-chip SerDes and starts external PHY ports at `NXGE_EXT_PHY_PORT_ST`. It defines Clause 45 device addresses for PMA/PMD and PCS, standard ID register offsets, and chip IDs for Broadcom 8704/8706, Marvell 88X201x, Teranetics TN1010, and NetLogic/AEL2020.

Family ID masks intentionally ignore revision/model bits for Broadcom, TN1010, and NLP2020 devices. Address-base constants cover Neptune, N2, Goa, alternate Goa port 1, NLP2020 RF/QSFP port layouts, and Maramba variants.

## Broadcom 5464R And 8704/8706 Support

For BCM5464R, the file defines MII register numbers 16 through 30 and bitfield unions for extended control/status, RX error, false carrier, RX-not-OK, expansion-register access, auxiliary control/status, interrupt status/mask, shadow/miscellaneous access, and test register 1.

For BCM8704-class 10G PHYs, it defines PMD, PCS, PHYXS, and user-space register offsets, including control/status, IDs, speed ability, package devices, transmit disable, receive signal detect, XGXS lane status, analog/user controls, optics digital control, RX polarity, and alarm status.

## Marvell, Teranetics, NetLogic, And Module Constants

Marvell 88X2011 definitions cover MMD addresses, PMA/PMD status, transmit disable, XGXS lane status, general control, LED blink/control fields, and helper macros for LED nibbles.

Teranetics TN1010 definitions cover PMA/PMD, PCS, PHYXS, autonegotiation, and vendor MMD1 registers. NetLogic/AEL2020 constants define PMA/PMD reset/link/signal-detect, optical setup, TX pre-emphasis, microcontroller control/start PC, PCS/PHYXS link/status/lane sync, GPIO module detect/action, and I2C snoop access to the transceiver.

SFP+/QSFP constants identify copper twinax and fiber connector types, QSFP MSA connector/length/low-power-mode registers, and a connector classification enum distinguishing fiber, copper shorter than 7m, and copper 7m or longer.

## Software Property Structures

`nxge_nlp_initseq_t` stores a PHY register/value initialization pair. `nxge_phy_mdio_val_t` stores device, register, and value triples. `nxge_phy_prop_t` wraps an array of MDIO triples with a count.

## Research Notes

The file contains no executable logic, but it centralizes hardware compatibility assumptions. Risk areas are mask correctness for PHY probing, MMD/device mismatch between PHY families, endian-sensitive bitfields, and duplicated/similar control typedef names for TN1010 PCS/PHYXS.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_phy_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_rxdma.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_rxdma.h

## Purpose

`nxge_rxdma.h` defines the NXGE receive-DMA software state model and RXDMA entry points. It builds on `nxge_rxdma_hw.h` and NPI RXDMA APIs to represent receive buffer rings, receive completion rings, RX mailboxes, RX buffer loaning, polling, statistics, and channel initialization/recovery.

## Data Structures

The file defines operational defaults for RX clock divider, RED/WRED thresholds, RCR interrupt threshold/timeout, RX posting batch size, buffer alignment, and copy-threshold policy. `nxge_rxbuf_threshold_t` controls how aggressively packets are copied versus loaned; `nxge_rxbuf_type_t` maps software buffer classes to RCR hardware buffer-size codes.

`nxge_rx_ring_stats_t` is the main per-RDC counter block. It tracks packets/bytes/errors, multicast/broadcast/no-buffer counters, buffer allocation/reuse/drop counters, hardware event counters, and an `rdc_errlog_t` containing prefetch/shadow parity logs plus completion error type.

`rx_msg_t` is the per-receive-buffer state object. It includes DMA memory, lock, owning device/ring, spare/free/reference state, free callback, byte accounting, block sizing, usage counters, buffer pointer, priority, shifted address, pool flag, associated mblk, and bcopy policy.

`rx_rcr_ring_t` models a receive completion ring: DMA allocation, stats, poll flag, config registers, lock, indices, descriptor pointers, RBR linkage, interrupt timeout/threshold, MAC ring handle, generation number, byte accumulator, interrupt group/vector references, and started state.

`rx_rbr_ring_t` models a receive buffer block ring: descriptor DMA, `rx_msg_t` array, DMA buffer array, RBR config/kick/logical-page registers, ring indices, block and packet-buffer sizing, RCR backpointer, optional sun4v workaround mappings, thresholds, bcopy policy, reference count, state, and allocation type.

## Interfaces

The exported functions cover channel lifecycle, RCR flush, reset, control/status setup, event-mask setup, channel enable, 32-bit/64-bit hardware mode setup, RX hardware start, ring/channel repair, MAC polling, register dumping, system error handling, error injection, RX memory pool allocation/free, and RX ring index lookup.

## Research Notes

This header is the software half of the RXDMA ABI. The highest-risk semantics are RX buffer loan/reference handling, `RBR_POSTING` to `RBR_UNMAPPING` transitions, RCR/RBR index wrap management, and coordination between interrupt mode and polling mode. The `RXBUF_START_ADDR` macro appears syntactically incomplete in the header as read, which may be hidden by non-use or historical build context.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_rxdma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_rxdma_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_rxdma_hw.h

## Purpose

`nxge_rxdma_hw.h` is the receive-DMA hardware register and descriptor ABI for Neptune/NIU. It defines FZC/DMC register offsets, masks, shifts, endian-aware register unions, RBR/RCR descriptors, mailboxes, WRED/discard counters, parity/error logs, RDMC debug access, FIFO diagnostics, and receive packet header formats.

## Global RXDMA Registers

The file begins with function-zero control registers for RX clock divider, default port-to-RDC mapping, RDC table entries, 32-bit addressing mode, port DRR weights, port FIFO usage, logical page partitioning, and WRED random initialization. Most registers are 64-bit CSRs with meaningful fields in the low 32 bits and `_BIG_ENDIAN` conditional layouts.

Logical page support uses common page-valid, mask, value, relocation, and handle registers per channel. RED/WRED support defines per-RDC parameter and discard-count registers with window/threshold fields for normal and synchronized thresholds.

## Ring And Descriptor ABI

`rx_desc_t` is the receive buffer block descriptor containing the posted block address. `rcr_entry_t` is the 64-bit completion descriptor containing buffer address, packet buffer size code, L2 length, DCF error, RX error code, promiscuous/noport flags, zero-copy flag, packet type, and multi-block indication.

The RBR registers configure descriptor base/length, three packet buffer sizes and valid bits, block size, kick count, status queue length/overflow, and hardware head. The RCR registers configure descriptor base/length, interrupt timeout/threshold, queue status, tail pointer, event mask, control/status, flush, and error logging.

## Error, Mailbox, And Debug State

`rx_dma_ent_msk_t` and `rx_dma_ctl_stat_t` describe the RXDMA interrupt mask and control/status bits. Events include config/RBR log page errors, RBR full/empty, RCR full/inconsistent, config errors, shadow full, pre-empty, WRED and port drops, prefetch/shadow parity, RCR timeout/threshold, data FIFO errors, ACK/response/byte-enable errors, and RBR timeout. `RX_DMA_CTL_STAT_WR1C` identifies write-one-to-clear bits.

`rxdma_mailbox_t` lays out the 64-byte mailbox image. `rx_disc_cnt_t` and `red_disc_cnt_t` count discards with overflow flags. `rdmc_par_err_log_t`, `rdmc_mem_addr_t`, `rdmc_mem_data_t`, and `rdmc_mem_access_t` support parity log and internal RDMC memory access. RX control/data FIFO state reports IPP/ZCP EOP errors and ID mismatch.

## Packet Header Formats

The file defines the two-byte RX packet header format 0 with input port, MAC check, class, VLAN, LLC/SNAP, noport, bad IP, TCAM hit, and transfer-zone validity. It also defines the 18-byte format 1 as byte-sized unions for TCAM match, hash hit/index/value, zero-copy flow ID, user data, and reserved fields.

## Research Notes

This is a dense hardware ABI file. Maintenance risks include incorrect bit masks, duplicated/misspelled mask macros, endian layout mistakes, confusing address low/high split handling, and incorrect write-one-to-clear behavior. RX correctness depends on strict agreement between this header, NPI register accessors, and `nxge_rxdma.h` ring bookkeeping.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_rxdma_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_sr_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_sr_hw.h

## Purpose

`nxge_sr_hw.h` defines the Neptune SerDes register map and bitfields for RX/TX common control, reset, power, tuning, synchronization, test, and glue-control registers. It is a low-level MDIO/ESR hardware description for programming four SerDes lanes A through D across multiple ports.

## Register Addressing

The header defines Neptune ESR device/base constants and raw register offsets for common control, reset control, RX/TX power control, misc power control, per-lane RX/TX control, tuning, sync character, test, glue controls, and additional tuning banks. Address macros convert byte offsets into the PRM-required halfword register addresses by shifting right by one and adding low/high word selectors.

Per-lane macros compute low/high addresses from lane `chan` with `0x20` spacing.

## Bitfield Groups

The common control unions expose reference clock frequency, transmit-data master lane, termination/tuning fields, and reverse-loopback reference selection. Reset and power-control unions provide per-port/per-lane RX reset, TX reset, RX LOS powerdown, RX powerdown, TX PLL powerdown, TX powerdown, PECL/PLL/misc powerdown, and clock-output powerdown bits.

Per-lane RX/TX control and tuning unions define receive present window, rise/fall control, stretch enable, bias, FIFO/test controls, VMUX/VPULSE, RX equalization, TX level/termination tuning, sync character/mask/polarity, test reference/selftest fields, LOS test/enable, fast resync, samplerate, threshold count, bit-lock time, init time, receiver/transmitter termination, and trim enable.

## Research Notes

This header has no functions and no state. Its main value is preserving hardware register semantics in a typed form. Risks are wrong low/high address calculations, applying lane macros to common registers, and changing bitfield definitions without matching the hardware PRM.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_sr_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txc.h

## Purpose

`nxge_txc.h` defines the NXGE transmit-controller software state, statistics, error log, and public TXC entry points. TXC is the transmit-side controller that binds transmit DMA channels to ports and monitors reorder/store-forward error state.

## Main Definitions

`TXC_DMA_MAX_BURST_DEFAULT` is set to 1530 bytes, described as the hardware team's recommended DRR max burst.

`txc_errlog_t` contains reorder (`txc_ro_states_t`) and store-forward (`txc_sf_states_t`) state snapshots from `nxge_txc_hw.h`. `nxge_txc_stats_t` counts packets stuffed/transmitted, reorder and store-forward correctable/uncorrectable errors, address/DMA/length failures, packet assembly dead events, reorder errors, and the captured error log.

`nxge_txc_t` stores TXC configuration and current values: DMA max burst, DMA length, training vector, debug selector, control/status, port DMA bitmap/list, and a pointer to TXC stats.

## Interfaces

The exported functions initialize/uninitialize TXC, bind/unbind a TDC to TXC, handle TXC system errors, and inject TXC errors for debug/testing.

## Research Notes

This file is a thin software-facing wrapper around the much larger `nxge_txc_hw.h` register ABI. The interesting correctness boundary is TXDMA-to-port binding and error recovery: TXC state must agree with `nxge_txdma.h` rings and TXC hardware reorder/store-forward diagnostics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txc_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txc_hw.h

## Purpose

`nxge_txc_hw.h` defines the transmit-controller hardware register ABI for NXGE/Neptune/NIU. It covers TXC port DMA enable masks, per-channel DRR parameters, global control/training/debug, port statistics, reorder and store-forward ECC controls/status/data, reorder state read/write controls, packet request counters, and TXC interrupt status/masks.

## Control And Scheduling Registers

The header defines `TXC_PORT_DMA_ENABLE_REG` plus 24-bit and N2 16-bit DMA-list layouts for binding TX DMA channels to TXC/ports. Offset macros compute per-port and per-channel FZC register addresses.

Core control registers include DMA max burst, DMA max length, global TXC control, N2 two-port control, training vector, debug select, max reorder depth per port, and per-port clear/stat controls.

## Statistics And ECC Diagnostics

`txc_pkt_stuffed_t` and `txc_pkt_xmit` expose packet assembly/reorder and packet/byte transmit counters. Reorder ECC and store-forward ECC sections each define control, status, and five data registers per port. The ECC control fields support disabling UE, forcing single/double-bit errors, and selecting first/second/last/all/alternate/one packet injection styles.

Reorder state registers expose TIDs in use, duplicate TID, unused TID, transaction timeout, FIFO space/watermark state, and `txc_ro_ctl_t` for fail-state clearing, failure capture flags, state read/write address, and state read/write completion bits.

## Interrupts

TXC interrupt status bits include store-forward correctable/uncorrectable error, reorder correctable/uncorrectable error, reorder error, and packet assembly dead. The file defines normal and debug interrupt status registers, a four-port interrupt mask, and an N2 two-port interrupt mask.

## Research Notes

This header is pure register metadata. High-risk fields are port/channel offset calculations, N2 versus four-port masks, ECC injection controls, and read/write state-machine bits in `txc_ro_ctl_t`. Some macros appear to refer to nonlocal or typo-like names such as `TXC_STATE0_REG` in offset macros; callers must be checked before changing them.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txc_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txdma.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txdma.h

## Purpose

`nxge_txdma.h` defines the NXGE transmit-DMA software ring model, transmit message bookkeeping, statistics, mailbox/ring aggregates, and TXDMA entry points. It sits above `nxge_txdma_hw.h` and NPI TXDMA accessors.

## Ring And Buffer State

The file defines port DMA bitmap access, reclaim defaults, full-ring marker policy, transmit load-balancing modes, ring empty/full helpers, descriptor index increment, and default DRR weight.

`tx_msg_t` tracks one transmit message or premapped buffer: DMA/bcopy/DVMA flags, buffer DMA state, DMA handles, linked-list pointer, original mblk, message size, byte usage, and descriptor head/tail indices.

`nxge_tx_ring_stats_t` tracks packets/bytes/errors, initialization/no-buffer events, mailbox and hardware errors, start/nocanput failures, message duplication/allocation/DMA bind/descriptor failures, underruns, header/DDI/DVMA packet classes, max pending descriptors, jumbo packets, and a TXDMA ring error log from the hardware header.

`tx_ring_t` is the core TDC software state. It includes descriptor DMA, message ring, TX hardware config/status/mailbox/logical-page registers, TXC max-burst state, online/offline flags, locking, MAC ring handle, taskq, channel configuration pointer, ring size/chunks, software and hardware indices, pending descriptor count, queueing state, software queue head/tail, interrupt group, stats, DVMA ring state, and optional sun4v workaround mappings.

## Interfaces

The exported functions cover channel lifecycle, DMA common setup, reset, event mask setup, control/status setup, channel enable, packet header reservation, DMA block counting, descriptor reclaim, offload header fill, 32-bit/64-bit mode, hardware start/stop/restart, ring/channel fixup, hardware kick, register dumps, hang detection/recovery, reclaim of all rings, error injection, and TX memory pool allocation/free.

## Research Notes

This header defines the transmit fast-path contract between MAC, DMA mapping, descriptor rings, and hardware. Key risk points are descriptor wrap/full logic, concurrent reclaim versus send, DVMA ring accounting, offline state transitions, hang detection thresholds, and correct construction of TX packet headers for checksum offload.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txdma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txdma_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txdma_hw.h

## Purpose

`nxge_txdma_hw.h` defines the transmit-DMA hardware ABI: logical page partitioning, addressing mode, packet descriptors, TX ring registers, event masks, control/status, mailbox format, error logs, packet header offload format, and debug/error-injection registers.

## Descriptor And Ring ABI

`tx_desc_t` is the 64-bit packet descriptor. It encodes source address, transfer length, gather pointer count, mark bit, and start-of-packet bit. `TX_MAX_GATHER_POINTERS` is 15, with a threshold of 8. The header documents a hardware bug that reduces max transfer length to 4076 and sets jumbo MTU at 9216.

TX ring registers configure descriptor base/length, head low, kick/tail, event mask, control/status, mailbox address high/low, prefetch state, ring error logs, interrupt debug, and control/status debug.

## Events, Control, And Mailbox

`tx_dma_ent_msk_t` and `tx_cs_t` define event mask/control status bits for packet partition error, config partition error, NACK packet read, NACK prefetch, prefetch buffer parity/ECC error, ring overflow, packet size error, mailbox error, marker bits, stop-and-go, mailbox state, reset state, last mark, and packet count.

`txdma_mailbox_t` is the 64-byte hardware mailbox image containing TX control/status, prefetch state, head, kick, error logs, and padding. Error logs capture transmit ring error address, code, multiple-error flag, and error-present flag.

## Packet Header Offload Format

`tx_pkt_header_t` defines the 16-byte internal packet header's first 64-bit word: padding, total transfer length, L4 checksum stuff/start, L3 start, IP header length, VLAN, LLC, IP version, and checksum packet type. Constants define L4 operations for no-op, full checksum, payload checksum, and SCTP CRC32, plus packet types for TCP, UDP, SCTP, and no-op.

## Research Notes

This file is central to TX data integrity. Audit-sensitive details include endian handling in descriptors, source address and transfer length masks, max transfer length enforcement, marker/interrupt semantics, write-one-to-clear control bits, and the relationship between software `tx_ring_t` indices and hardware head/tail/wrap fields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_txdma_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_virtual.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_virtual.h

## Purpose

`nxge_virtual.h` defines virtualization/shared-resource control operations and state bits for the Neptune/NXGE driver. It is used when multiple functions or domains coordinate access to shared NIU registers, locks, interrupt masks, and common configuration.

## Main Definitions

`nxge_ctl_enum_t` enumerates control operations: query NIU type, get attributes, get/set hardware properties, get/set/update shared registers, acquire blocking or try locks, free locks, set shared registers under lock, clear shared register bits, and clear bits without lock.

Common shared-state bits describe valid/busy state, initialization start/done, TCAM busy, VLAN busy, and NIU PCI reset. `NXGE_SR_FUNC_BUSY_SHIFT` and `NXGE_SR_FUNC_BUSY_MASK` define a shared-register function-busy field.

Configuration category bits identify common TXDMA, RXDMA, RXDMA group, classifier, and quick configuration operations.

## Interfaces

The header exports `nxge_intr_mask_mgmt()` for interrupt-mask management and `nxge_virint_regs_dump()` for virtual interrupt register diagnostics.

## Research Notes

This file has no structs beyond the enum and no implementation. Its correctness depends on consistent shared-register locking across the driver and firmware/hypervisor environment. Race-sensitive areas are busy-bit ownership, clear-without-lock operations, and initialization completion signaling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_virtual.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_zcp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_zcp.h

## Purpose

`nxge_zcp.h` is the software-facing header for the NXGE zero-copy hardware block. It wraps the ZCP hardware definitions with statistics, error-log state, and initialization/recovery/debug entry points.

## Main Definitions

`zcp_errlog_t` stores a captured `zcp_state_machine_t` snapshot. `nxge_zcp_stats_t` tracks total errors and inits plus hardware-specific error counters: RRFIFO underrun/overrun, response FIFO uncorrectable error, buffer overflow, static/dynamic/buffer table parity errors, transfer-table programming and index errors, access failures, CFIFO ECC, and error log.

`nxge_zcp_t` stores ZCP config, interrupt config, and a pointer to stats.

## Interfaces

The exported functions initialize ZCP, inject ZCP errors, and perform fatal-error recovery.

## Research Notes

This is a compact software wrapper for `nxge_zcp_hw.h`. The important behavior lives in consumers that program ZCP tables and recover from ZCP fatal errors. Stats names map directly to interrupt/status bits in the hardware header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_zcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_zcp_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_zcp_hw.h

## Purpose

`nxge_zcp_hw.h` defines the Neptune zero-copy hardware ABI. It describes ZCP configuration/status/mask registers, buffer-address-map and destination-region controls, RAM access/data registers, CFIFO reset/ECC state, transfer table entry formats, RAM selectors, training/state-machine registers, packet zero-copy header state, and ECC injection control.

## Configuration And Interrupts

The top-level registers include config, interrupt status, interrupt test, interrupt mask, BAM region controls for 4/8/16/32 buffer regions, DST region controls for matching sizes, RAM data and byte-enable/access registers, training vector, state machine, check-bit data, CFIFO reset, and per-port CFIFO ECC registers.

`zcp_config_reg_t` exposes 32-bit mode, debug selector, RDMA threshold, ECC/parity check disable, buffer request disables, and zero-copy enable. `zcp_int_stat_reg_t` / mask layout covers RRFIFO underrun/overrun, response FIFO uncorrectable error, buffer overflow, static/dynamic/buffer table parity, transfer-table program/index errors, and CFIFO ECC for ports 0 through 3.

## BAM/DST And Transfer Table Entries

`zcp_bam_region_reg_t` defines logical offset, first/last zero-copy flow IDs, range-check enable, and LOJ. `zcp_dst_region_reg_t` defines destination offset.

`tte_sflow_attr_t` is the static flow table entry with five quadwords containing RDC table offset, buffer size/count, ULP end, ring base/size, skip, transfer mode, unmap controls, busy, TOQ, and data nibble fields. `tte_dflow_attr_t` is the dynamic flow entry with mapped-in state, anchor sequence, anchor buffer/offset flags, ULP-end/unmap status, error status, write pointer, head-of-queue, prefetch flag, and data nibble.

## RAM Access And Packet State

`zcp_ram_access_t` selects read/write, ZCFID, RAM selector, and CFIFO. RAM selectors cover eight BAM banks, static/dynamic transfer tables, and four CFIFOs. `zcp_ram_benable_t` provides byte enables. `zcp_ram_data_t` overlays static and dynamic table entries.

`zcp_hdr_t` is a software header describing a zero-copy flow packet: flow ID, TCP header/payload length, head of queue, first buffer offset, end-of-buffer reach flag, DMA window crossing type, and window buffer offset.

## Research Notes

ZCP is table-driven and stateful; mistakes in transfer table bitfields can cause DMA into the wrong buffer or failed auto-unmap behavior. Audit-sensitive areas are RAM access busy/read-write sequencing, byte-enable masks, BAM/DST range checks, ULP-end/unmap flags, and CFIFO reset/ECC handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_zcp_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/objfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/objfs.h

## Purpose

`objfs.h` is the public header for illumos object filesystem metadata. It defines the objfs root path, a helper to recover a module ID from an objfs inode number, and the private `.info` payload structure exposed by objfs data files.

## Main Definitions

`OBJFS_ROOT` is `/system/object`. `OBJFS_MODID(ino)` masks the low 32 bits of an inode number to obtain the module ID, with undefined results for the root inode. `objfs_info_t` currently contains one field, `objfs_info_primary`, representing the primary/private data stored in the `.info` section.

## Integration Notes

The implementation header `objfs_impl.h` builds inode numbers as a high 32-bit type plus low 32-bit module ID. This public header exposes only the low-bit module ID extraction, not the internal type encoding.

## Research Notes

This is a small public contract. Compatibility risk is high if `objfs_info_t` or `OBJFS_ROOT` changes, because consumers may rely on the path and structure layout.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/objfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/objfs_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/objfs_impl.h

## Purpose

`objfs_impl.h` defines the internal objfs VFS/vnode object model. Objfs represents kernel modules and associated object data using generic filesystem (`gfs`) directory/file nodes and stable synthetic inode numbers.

## Main Structures

`objfs_vfs_t` stores the root vnode for a mounted objfs instance. The header declares common vnode operation helpers for directory open/access, common close, and common getattr, plus `objfs_nobjs()` for object count support.

Inode construction is defined by `OBJFS_INO(modid, type)`, which places a vnode type in the high 32 bits and the module ID in the low 32 bits. The root inode is `0xffffffff`. Module object directories use type 0, so their inode value equals the module ID.

The root node is a `gfs_dir_t`. Object directory nodes (`objfs_odirnode_t`) embed a `gfs_dir_t` and a `struct modctl *`. Data nodes (`objfs_datanode_t`) embed a `gfs_file_t`, an `objfs_info_t`, and a generation count captured when opened.

## Interfaces

The header declares operation templates and vnodeops pointers for root, object directory, and data file vnode types, plus constructors: `objfs_create_root(vfs_t *)`, `objfs_create_odirnode(vnode_t *, struct modctl *)`, `objfs_data_init()`, and `objfs_create_data(vnode_t *)`.

## Research Notes

The file is internal and depends on `modctl`, VFS/vnode, GFS, and public objfs definitions. Correctness depends on synthetic inode stability, module generation handling for data files, and keeping GFS node embedding as the first struct member where expected by GFS helpers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/objfs_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ontrap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ontrap.h

## Purpose

`ontrap.h` defines the kernel `on_trap()` / `no_trap()` exception-protection interface and the `on_trap_data_t` stack record. It is not a public DDI interface. It protects selected code regions from machine exceptions by returning through a setjmp-like mechanism.

## Semantics

`on_trap()` returns zero when installed normally and nonzero when returning after a protected exception. Callers must test only zero versus nonzero. `no_trap()` pops the active trap-protection record; callers must invoke it even after an exception return because catching a trap does not modify `t_ontrap`.

Nested calls are supported through a linked list rooted in the current thread's `t_ontrap`. Reusing the same `on_trap_data` address modifies the top stack element in place, allowing loop usage without pushing duplicate records. `no_trap()` is permitted on an empty stack and only changes thread trap state.

Protection bits are `OT_DATA_ACCESS`, `OT_DATA_EC`, and on x86 `OT_SEGMENT_ACCESS`. Unsupported protection types must panic rather than silently continue unprotected.

## Data Structure And Interfaces

`on_trap_data_t` stores active protection bits, actual trap bit, optional trampoline PC, longjmp label buffer, previous record pointer, access handle, and reserved padding. In kernel builds, it declares `on_trap()`, `no_trap()`, and the default `on_trap_trampoline()`.

## Research Notes

This interface is dangerous by design. Audit focus should be balanced `on_trap()`/`no_trap()` pairs, stack lifetime of `on_trap_data_t`, platform support for requested bits, and ensuring protected regions do not leak locks/resources when an exception path longjmps back.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ontrap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/open.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/open.h

## Purpose

`open.h` defines illumos device-driver open/close type constants. These constants let drivers distinguish why a device is being opened or closed and maintain correct per-minor usage state.

## Open Types

The file defines `OTYPCNT` as 5 and the five open types: `OTYP_BLK` for block special files, `OTYP_MNT` for filesystem mount/unmount, `OTYP_CHR` for character special files, `OTYP_SWP` for swap devices, and `OTYP_LYR` for layered driver opens/closes without a file directly open on the lower device.

The first four types may have many opens but only one close on last close for that minor/type, so a boolean state flag can work. `OTYP_LYR` opens and closes are always paired, so drivers should use counters.

## Research Notes

This is a stable kernel ABI header. Misinterpreting the close protocol is the main bug risk: using a boolean for layered opens or a counter-only model for last-close types can cause premature detach, leaked holds, or incorrect busy checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/open.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/openpromio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/openpromio.h

## Purpose

`openpromio.h` defines the legacy OpenPROM ioctl data structure and ioctl command numbers used to query and manipulate OpenBoot/OpenPROM properties and device-tree paths.

## Data Structure

`struct openpromio` contains `oprom_size` and a union payload used either as a byte array for property names/values or as an integer node/length field. Macros alias the union as `oprom_array`, `oprom_node`, and `oprom_len`.

The header documents a historical `SETOPT` compatibility issue: old driver and eeprom behavior used `strlen()` rather than `oprom_size`, so `OPROMSETOPT2` exists as the working interface for non-ASCII or size-sensitive property values.

`OPROMMAXPARAM` is 32768, four times the largest noted 8K property size.

## Ioctls

Ioctl constants are built from `OIOC`. Commands include get/set/next option, raw config ops for next/child/getprop/nextprop/proplen, console/framebuffer/boot/version queries, path-to-driver and devfs/prom path conversion, deprecated 64-bit readiness, current node setting, snapshot/copyout, ASR key/export operations, and bootpath retrieval.

Console return bits identify keyboard stdin, framebuffer stdout, and OpenPROM support.

## Research Notes

The ABI intentionally uses void-typed ioctls because copy sizes vary and the driver handles copyin/copyout manually. Risk areas are buffer sizing, null termination versus `oprom_size`, and command compatibility with old firmware/userland expectations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/openpromio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay.h

## Purpose

`overlay.h` defines the public ioctl ABI for illumos overlay network devices. It exposes create/delete/property/activation/status operations and the fixed-size structures passed through the overlay control device.

## Ioctl ABI

The ioctl commands are `OVERLAY_IOC_CREATE`, `DELETE`, `PROPINFO`, `GETPROP`, `SETPROP`, `NPROPS`, `ACTIVATE`, and `STATUS`, all based on `OVERLAYIOC()`.

`overlay_ioc_create_t` supplies a datalink ID, virtual network ID, and encapsulation plugin name. Other structs identify a link for activation, deletion, property count, property info, property get/set, or status.

Property info includes property ID/name, type, permissions, default value/size, possible value size, and possible values. Property get/set uses link ID, ID/name, raw value buffer, and value size. Status returns `OVERLAY_I_OK` or `OVERLAY_I_DEGRADED` plus a status message.

## Research Notes

This file is a user/kernel ABI. Changes to structure sizes, fixed buffer lengths, enum values, or ioctl numbers are compatibility-sensitive. Validation-sensitive fields include property sizes, encapsulation name length, and degraded status message handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_common.h

## Purpose

`overlay_common.h` contains small shared overlay networking definitions used by both public overlay ioctls and internal overlay implementation/plugin code.

## Definitions

`overlay_target_mode_t` distinguishes no target, point target, and dynamic target modes. `overlay_plugin_dest_t` describes the destination tuple fields required by an encapsulation plugin: Ethernet, IP, port, or mask combinations.

`overlay_prop_type_t` defines property payload types: signed integer, unsigned integer, IP address, and fixed-size string. `overlay_prop_prot_t` defines required/read/write permission flags and combined masks.

The fixed ABI sizes are `OVERLAY_PROP_NAMELEN` 64, `OVERLAY_PROP_SIZEMAX` 256, and `OVERLAY_STATUS_BUFLEN` 256.

## Research Notes

This file is ABI glue. The important constraints are stable enum values and fixed property/status buffer sizes. Property permission masks are bitfields, so validation should mask unknown bits with `OVERLAY_PROP_PERM_MASK`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_impl.h

## Purpose

`overlay_impl.h` defines the internal kernel structures and subsystem interfaces for illumos overlay devices. It connects overlay plugins, socket multiplexers, target resolution, MAC device state, fault-management status, property handling, and transmit/receive coordination.

## Core Structures

`overlay_plugin_t` stores registered encapsulation plugin metadata, ops, properties, ID size, flags, destination requirements, active count, and list linkage. Mutable fields are protected by `ovp_mutex` or global plugin locking as commented.

`overlay_mux_t` represents a shared socket/mux instance for a plugin and socket tuple. It owns the kernel socket, protocol/address metadata, active instance count, and an AVL tree of devices.

`overlay_target_t` stores point or dynamic target-resolution state, with teardown flag, open count, condition variable, destination mode/type/ID, and either a point target or dynamic refhash/AVL state.

`overlay_dev_t` is the central per-overlay device object. It tracks MAC handle, plugin, datalink ID, plugin private pointer, refcount, MTU, flags, RX/TX counts, mux pointer, virtual network ID, mux AVL node, target pointer, and fault-management message.

`overlay_target_entry_t` tracks dynamic destination entries: locks, refhash/AVL/list linkage, pending/valid/drop flags, MAC address, target/device pointers, destination socket address, queued blocked mblks, outstanding size, and valid timestamp.

## Internal Interfaces

The header declares the overlay control name, a DTrace-backed `OVERLAY_FREEMSG()` macro, global `overlay_dip`, MAC transmit entry point `overlay_m_tx()`, device iteration, plugin lookup/release/walk lifecycle, I/O start/done accounting, mux lifecycle/open/close/add/remove/transmit, property initialization, target open/ioctl/close/free/lookup/quiesce lifecycle, fault-management degrade/restore, and datalink-ID hold/release helpers.

Target lookup returns `OVERLAY_TARGET_OK`, `OVERLAY_TARGET_DROP`, or `OVERLAY_TARGET_ASYNC`.

## Research Notes

This header encodes the overlay subsystem's locking and lifetime model. Audit-sensitive areas include device refcount and stop-mask transitions, TX/RX active counters, mux device AVL membership, plugin active counts, target-entry pending queues, async lookup completion, and degradation metadata updates while traffic is being dropped.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_impl.h -->