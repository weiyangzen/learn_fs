# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_blocks_linux_driver.h lines 32826-37748

## Purpose

This chunk is a generated Gaudi2 Linux-driver block-map slice for the NIC configuration/MMIO aperture. It contains no executable code; it exports symbolic block windows used by the HabanaLabs Gaudi2 driver to locate NIC queue-manager, user-mapped doorbell/completion, packet-processing, MAC/PHY, SerDes, and port blocks.

The covered range begins in the middle of the `NIC5_QPC0` DB FIFO completion-index update address table and ends in the middle of the `NIC9_UMR0_14` user-mapped region. Within this range there are 4,923 `#define` entries: 1,641 `mm..._BASE` macros, 1,641 `..._MAX_OFFSET` macros, and 1,641 `..._SECTION` macros. The first complete base macro in the chunk is `mmNIC5_QPC0_DBFIFO7_CI_UPD_ADDR_BASE` at `0x569F758ull`; the last complete base macro is `mmNIC9_UMR0_14_COMPLETION_QUEUE_CI_1_BASE` at `0x588E180ull`. The line range also includes the beginning of `mmNIC9_UMR0_14_SPECIAL_BASE` and `mmNIC9_QM_DCCM0_BASE` just after the requested end, but those entries are outside this chunk's final complete triplet set.

## Important APIs, Types, And Definitions

This chunk does not define C functions, structs, enums, or runtime APIs. Its interface is the generated preprocessor namespace included through `include/gaudi2/asic_reg/gaudi2_regs.h`.

Each hardware window is represented by a triplet:

- `mm<block>_BASE`: 64-bit base address in the Gaudi2 register address map.
- `<block>_MAX_OFFSET`: maximum register offset associated with that generated block.
- `<block>_SECTION`: generated section size or stride reservation for the block.

Major block families covered here are:

- `NIC5_QPC0` tail and `NIC5_QPC1`: QPC DB FIFO completion-index update address entries, including numbered DB FIFO channels, secure and privileged FIFO update entries, AXUSER subwindows for congestion queues, RX/TX WQEs, DB FIFO, event queues, error FIFO, QPC responses/requests, and `SPECIAL` windows.
- `NIC5_UMR1`, `NIC6_UMR0/UMR1`, `NIC7_UMR0/UMR1`, `NIC8_UMR0/UMR1`, and the start of `NIC9_UMR0`: fifteen UMR blocks per UMR half where complete, each with `UNSECURE_DOORBELL0`, `UNSECURE_DOORBELL1`, `COMPLETION_QUEUE_CI_0`, `COMPLETION_QUEUE_CI_1`, and `SPECIAL` windows. The UMR blocks use a visible `0x1000` stride between block IDs.
- `NIC5`, `NIC6`, `NIC7`, and `NIC8` queue-manager regions: `QM_DCCM0/1`, `QM_ARC_AUX0/1`, `QM0`, `QM1`, per-QM `QMAN_WR64_BASE_ADDR0..15`, AXUSER secured/non-secured windows, debug HBW/LBW windows, CGM, and `SPECIAL` windows.
- `NIC5`, `NIC6`, `NIC7`, and `NIC8` datapath blocks: `TMR`, `RXB_CORE`, `RXE0`, `RXE1`, `RXE0_AXUSER`, `RXE1_AXUSER`, `TXS0/1`, `TXE0/1`, `TXB`, `MSTR_IF`, `TX_AXUSER`, `SERDES0/1`, and `PHY`.
- `PRT5` through `PRT8` port/MAC blocks: `MAC_AUX`, `MAC_CORE`, and their `SPECIAL` windows.
- `NIC5` through `NIC8` MAC blocks: `MAC_RS_FEC`, global statistic control/RX/TX/RSFEC stats, and per-channel `MAC_PCS`, `MAC_128`, and `MAC_AN` windows for channels 0-3.

The complete repeated NIC6-NIC8 portions are structurally symmetric. NIC5 is partial at the start because earlier `NIC5_QPC0`, `NIC5_UMR0`, `NIC5_QM0`, and related entries are in preceding chunks. NIC9 is partial at the end because this chunk stops during `NIC9_UMR0`; its queue-manager, datapath, MAC, and port entries continue later.

## Control Flow

There is no runtime control flow in this header chunk. Its compile-time flow is:

1. `gaudi2_regs.h` includes `gaudi2_blocks_linux_driver.h`.
2. Gaudi2 C files include the aggregated register definitions through private ASIC headers.
3. Runtime code uses the generated base macros directly, or uses them as arithmetic anchors for repeated blocks.
4. MMIO helpers, user-mapping setup, and security setup operate on the computed addresses.

The surrounding driver treats many of these blocks as regular arrays rather than individually naming every generated macro. For example, UMR user mappings are derived from `mmNIC0_UMR0_0_UNSECURE_DOORBELL0_BASE` plus NIC, QM, and UMR strides, while the explicit per-NIC macros in this chunk document the generated map that those stride calculations must match.

## State And Persistence Behavior

The header owns no software state and persists nothing. Its constants become part of the compiled driver's hardware contract for a specific Gaudi2 register map.

The named hardware windows do hold device state when accessed by consuming code:

- UMR doorbell and completion-queue consumer-index windows expose user-facing doorbell/CQ state used for NIC submission/completion paths.
- QPC DB FIFO CI update address windows point the NIC queue-pair controller at completion-index update targets for DB FIFO channels.
- Queue-manager `QMAN_WR64_BASE_ADDR*`, AXUSER, debug, and CGM windows configure NIC QMs and affect command submission, security attributes, and diagnostics.
- RX/TX datapath, MAC statistics, FEC, PCS, autonegotiation, PHY, and SerDes windows expose live NIC link, packet, and error state.

That hardware state persists until changed by driver initialization, firmware, user doorbell writes through mapped regions, link-management flows, or reset. The header's role is only to name the correct addresses.

## Dependencies

- `include/gaudi2/asic_reg/gaudi2_regs.h` is the integration header that includes this block-map header.
- Per-register generated headers supply offsets inside many of these block windows. This file supplies coarse block bases and section sizes; it does not define individual register fields.
- `gaudi2.c` consumes NIC QM, ARC AUX, and DCCM bases in static maps such as queue-ID base tables and ARC CPU base tables. The visible consumers include `mmNIC5_QM0_BASE`, `mmNIC5_QM1_BASE`, `mmNIC6_QM0_BASE`, `mmNIC7_QM1_BASE`, `mmNIC8_QM0_BASE`, and related ARC/DCCM bases.
- `gaudi2_user_mapped_blocks_init()` derives user-visible NIC UMR mappings from the NIC UMR address pattern and publishes each block with `HL_BLOCK_SIZE`.
- `gaudi2_security.c` uses NIC address bounds such as `mmNIC5_TX_AXUSER_BASE` through `mmNIC5_MAC_CH3_MAC_PCS_BASE + HL_BLOCK_SIZE` to program LBW range registers, and uses UMR/QPC ranges elsewhere to decide which NIC registers can be unsecured.
- Driver MMIO helpers such as `WREG32()` and `RREG32()` ultimately use these constants after base/offset arithmetic.

## Integration Points

The highest-value integration points are address-map consumers that assume regularity across NIC instances:

- Queue ID mapping: Gaudi2 queue IDs for NIC engines map four queues at a time to `NICx_QM0_BASE` or `NICx_QM1_BASE`. The complete NIC6-NIC8 portions in this chunk provide the bases for queue IDs 12-17, and NIC5 entries cover queue ID 11 for `QM1` while `QM0` appears in an earlier chunk.
- ARC management: NIC queue-manager ARC AUX and DCCM bases are indexed by `CPU_ID_NIC_QMAN_ARC*`. The chunk includes NIC5 `QM_ARC_AUX1`/`QM_DCCM1`, complete NIC6-NIC8 `QM_ARC_AUX0/1` and `QM_DCCM0/1`, and prepares the next NIC9 DCCM range immediately after the chunk.
- User mapping: UMR windows are exposed to userspace as fixed-size blocks. The generated `UNSECURE_DOORBELL*` and `COMPLETION_QUEUE_CI_*` windows are the address-map evidence behind that exported ABI.
- Security: range-register setup secures or unsecures large NIC configuration spans using the first TX AXUSER block and a MAC-channel endpoint. Per-register security allowlists also rely on UMR and QPC windows having exact bases and strides.
- NIC link and telemetry handling: MAC global statistic, RS-FEC, channel PCS/MAC/autonegotiation, PHY, and SerDes windows are the block anchors for link status, error counters, and bring-up diagnostics.

## Risks And Edge Cases

- The chunk boundaries are partial. It starts after `NIC5_QPC0_DBFIFO0..6` and ends before the full `NIC9_UMR0_14_SPECIAL` triplet and all later NIC9 blocks. Per-file reconciliation must combine adjacent chunks before making complete-file claims.
- Generated triplets must stay aligned. A missing `BASE`, `MAX_OFFSET`, or `SECTION` companion can break scripts or code that expects one triplet per block.
- Arithmetic consumers depend on regular strides. UMR blocks visibly advance by `0x1000`; DB FIFO CI update entries advance by `0x8`; RXE AXUSER CQ entries advance by `0x50`; QMAN WR64 base-address entries advance by `0x8`. A bad generated literal may compile cleanly but map the driver to the wrong NIC register window.
- Security exposure is sensitive. Incorrect UMR/QPC/MAC bounds can either expose privileged NIC configuration to userspace or block required user doorbell/completion accesses.
- Many names are near-duplicates across NIC instances and QM halves. Manual edits or review-by-eye are error-prone, especially around `UMR0` versus `UMR1`, `QM0` versus `QM1`, and `RXE0` versus `RXE1`.
- `MAX_OFFSET` and `SECTION` are not always the same size. Consumers should not infer one from the other without checking the generated values.

## Test Signals

- Build coverage for Gaudi2 driver files that include `gaudi2_regs.h` will catch renamed or missing macros referenced by `gaudi2.c`, `gaudi2_security.c`, and related NIC code.
- Static generated-map checks should verify this chunk has 1,641 complete triplets and that each `mm..._BASE` has matching `..._MAX_OFFSET` and `..._SECTION` macros in the same line range.
- Pattern checks should validate repeated strides: UMR block IDs at `0x1000`, DB FIFO CI update address entries at `0x8`, QMAN WR64 base entries at `0x8`, and RXE AXUSER CQ windows at `0x50`.
- Runtime smoke signals include successful NIC queue-manager initialization, user doorbell mapping, completion-queue CI updates, and NIC link bring-up for NIC5-NIC8 plus the early NIC9 UMR range.
- Security tests should exercise LBW range-register programming and UMR/QPC access policy, because failures here can surface as user MMIO faults, blocked doorbell writes, or unexpectedly accessible privileged registers.
