# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_reg.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004368`: lines 1-4702, `Docs/researches/chunks/subset-b-004368_research.md`
- `subset-b-004369`: lines 4703-7778, `Docs/researches/chunks/subset-b-004369_research.md`

## Chunk Research

### subset-b-004368: lines 1-4702

# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_reg.h lines 1-4702

## Scope

This chunk covers the start of the Broadcom/QLogic Everest `bnx2x` hardware register map through the first timer-register definitions. It is a macro-only header: there are no C functions or structs in this range. The content defines register offsets, register-array base addresses and sizes, status/mask bits, access semantics, and hardware comments for major device blocks used by the `bnx2x` Ethernet driver.

The covered block families include ATC, BRB1, CCM, CDU, CFC, CSDM, CSEM, DBG, DMAE, DORQ, HC, IGU, MCP/MCPR, MISC/AEU, MSTAT, NIG, PBF, PB, PGLUE_B, PRS, PXP, PXP2, QM, SEM, SRC, TCM, and the beginning of TM. The full header continues beyond this chunk with more TM and later register/address families, so whole-file conclusions about all `bnx2x_reg.h` macros must be reconciled with following chunks.

## Purpose and Major Responsibilities

- Provide the canonical numeric hardware addresses used by `REG_RD()`, `REG_WR()`, `REG_RD_DMAE()`, `REG_WR_DMAE()`, and other low-level MMIO helpers throughout the `bnx2x` driver.
- Document hardware access classes in comments: read-only, read-clear, read/write, statistics clear-on-read, write-only, wide-bus multiword access, and write-1-to-clear behavior.
- Define parity, interrupt, attention, and clear-on-read status registers for many internal blocks. These macros drive error collection, parity masking, recovery, and diagnostic paths.
- Define queueing, buffering, flow-control, and scheduler registers for packet ingress/egress: BRB1 pause/full/LLFC thresholds, PBF queue credits and watermarks, NIG MAC/BRB/PBF enable paths, PRS parser configuration, QM VOQ/PQ mapping and credit registers, and PXP2 PCI request bandwidth controls.
- Define context-manager and storm-interface controls for the connection managers (`CCM`, `TCM`), connection/final-context memories (`CDU`, `CFC`), and DMA/storm blocks (`CSDM`, `CSEM`).
- Define PCIe, virtualization, and function-level-reset surfaces in PGLUE/PXP/PXP2: inbound interrupt tables, BAR/config-space redirection helpers, BME/FID/VF permission diagnostics, FLR dirty bits, ATS/ATC error details, and per-VF/PF request violation registers.
- Define MISC/AEU attention routing and latch control used to map block-level hardware/parity events into function, MCP, NIG gate, and PXP gate outputs.
- Define MCP and NVM register addresses used by management firmware and ethtool flash/NVM paths.

## Important Register Families

- `ATC_*` and `ATC_REG_*`: address-translation cache initialization and interrupt/parity status. `ATC_REG_ATC_INIT_ARRAY` starts valid-bit reset, `ATC_REG_ATC_INIT_DONE` reports completion, and status bits identify address errors, translation completion errors, and GPA multiple hits.
- `BRB1_REG_*`: buffer receive block controls. This group covers pause/full XON/XOFF thresholds, per-MAC and per-class guaranteed buffer space, LLFC high/low thresholds, occupancy/statistics counters, LL RAM, parity/interrupt masks, and `BRB1_REG_FREE_LIST_PRS_CRDT`, whose comment warns that the first post-reset RBC access must be a write and later writes can hang the device.
- `CCM_REG_*` and `TCM_REG_*`: connection-manager register sets for C and T directions. They expose interface enables to storm, QM, CFC, CDU, SDM, PBF/PRS, timers, and SEM blocks; initial credits; WRR weights; physical queue-number tables; context-load sizes; error/event IDs; and XX-protection tables, descriptor tables, credit limits, and overflow event IDs.
- `CDU_REG_*` and `CFC_REG_*`: context database and connection-finalization controls. `CDU_REG_L1TT`, `CDU_REG_MATT`, `CDU_REG_MF_MODE`, and check masks configure context translation/validation. `CFC_REG_CID_CAM`, `CFC_REG_INFO_RAM`, `CFC_REG_LINK_LIST`, and activity counters represent hardware-owned connection state tables, with explicit size macros used by diagnostics.
- `CSDM_REG_*` and `CSEM_REG_*`: completion storm DMA and C storm execution/register memory. The SDM registers provide timer ticks, producer/consumer start addresses, command counters, PXP credit/init state, sync-empty signals, enable bits, and parity/interrupt registers. The SEM registers include arbiter elements, thread scheduling status, interrupt tables, fast/passive memory, PRAM, and enable/disable controls.
- `DMAE_REG_*`: DMA engine command memory, command count (`DMAE_REG_CMD_MEM_SIZE`), CRC seeds, PCI/GRC interface enables, PXP request credit, channel `GO_C*` doorbells, and parity/interrupt registers.
- `DORQ_REG_*`: doorbell request queue control, including queue thresholds and fill levels, normal/DPM/VF CID address calculations, VF usage counters and limits, short/normal command headers, aggregate commands, response credits, and parity/interrupt registers.
- `HC_REG_*` and `IGU_REG_*`: legacy host-coalescing and interrupt-generation units. They define configuration bits, attention addresses, command registers, producer/consumer memory, MSI/MSI-X/PBA state, mapping memory, status-block cleanup, pending/write-done bits, timer masking, and PF/VF interrupt configuration addresses.
- `MCP_REG_MCPR_*` and `MCP_A_REG_MCPR_SCRATCH`: management-controller register offsets for scratch memory, NVM arbitration/read/write/command, GPIOs, access lock, IMC commands, and CPU program-counter observation.
- `MISC_REG_*`: AEU attention after-invert registers, per-output AEU enable registers, latch clear registers, GPIO/SPIO control, clock/PLL controls, reset registers, path/port strap overrides, shared-memory address, WOL outputs, and miscellaneous parity/interrupt registers.
- `NIG_REG_*`: network interface gateway registers for MAC/BRB/PBF ingress and egress enables, LLH classification tables, LLH function/VLAN memory, pause/LLFC/PFC control, LED controls, TimeSync/PTP host buffers and rule masks, NIG interrupt/parity status, TX arbitration priority/WFQ credits, and MAC mode/status paths.
- `PBF_REG_*` and `PB_REG_*`: packet buffer flow-control and parity/interrupt state. PBF entries configure queue enables, init credits, pause behavior, thresholding, task-queue counters, line occupancy/freed counters, VLAN types, and per-interface enables.
- `PGLUE_B_REG_*`: PCIe glue registers for config-space and FLR attention, SR-IOV dirty bits, inbound interrupt table setup for SDM blocks, zone offsets for PF/VF queue/legacy memory, VF length and GRC-space violation diagnostics, RX/TX error detail capture, tag usage, and latched error clearing.
- `PRS_REG_*`: parser setup for context regions, CFC load/search credits, CM headers and event IDs for packet/flush/no-match paths, Ethernet/VLAN/FCoE type parsing, required/allowed L2 header maps, CIDs, packet counters, serial-number debug status, and parser parity/interrupt registers.
- `PXP_REG_*` and `PXP2_REG_*`: PCIe host and request-side controls. These include interrupt/parity status, permission tables, doorbell/internal-write discard controls, PGLUE configuration windows, inbound interrupt tables, pretend-function registers, PSWRQ/PXP2 read/write bandwidth parameters, ILT first/last ranges, endian/swap modes, MPS thresholds, on-chip address-translation windows, request-queue counters, and read engine init/debug status.
- `QM_REG_*`: queue manager state, queue/VOQ/physical queue mapping, byte/task/VOQ credit controls, WRR weights, PF enable/usage counters, context registers, queue status, overflow status, pointer/base tables, and parity/interrupt registers. Many registers have `_EXT_A` variants for extended queue ranges.
- `SRC_REG_*`: searcher/RSS-related registers: RSS keys, search keys, hash-bit count, free-list pointers/counts, E1H multi-function enable, soft reset, and parity/interrupt status.
- `TM_REG_*`: the beginning of timer manager controls: client input enables, context regions, credit-counter load values, real-time counter enable, timer state-machine enable, linear timer logic address/max-active-CID, and scan statistics.

## Important APIs, Types, and Functions

This chunk defines preprocessor constants only. It does not declare callable APIs, data types, inline helpers, or executable control flow. The important "API" is the symbolic register namespace itself:

- `*_REG_*` macros are byte offsets in the device's GRC/MMIO register space, or offsets within a block base for repeated blocks such as `PB_REG_*`.
- `*_SIZE` macros describe how many entries diagnostic code can walk in register-backed memories, for example `CFC_REG_ACTIVITY_COUNTER_SIZE`, `CFC_REG_INFO_RAM_SIZE`, `CFC_REG_LINK_LIST_SIZE`, `DMAE_REG_CMD_MEM_SIZE`, `CCM_REG_XX_DESCR_TABLE_SIZE`, and `TCM_REG_XX_DESCR_TABLE_SIZE`.
- Bit-mask macros such as `ATC_ATC_INT_STS_REG_*`, `HC_CONFIG_*`, `MISC_AEU_GENERAL_MASK_REG_*`, `NIG_LLH*_BRB1_DRV_MASK_*`, `PGLUE_B_PGLUE_B_INT_STS_REG_*`, and `PXP2_PXP2_INT_*` give the driver named fields for status checking and mask programming.
- Address-family macros are consumed by hardware-access helpers defined outside this header. The direct users in this driver tree include `bnx2x.h` including `bnx2x_reg.h`, `bnx2x_init.h` parity and attention setup, `bnx2x_ethtool.c` register tests and NVM access, `bnx2x_cmn.h/.c` interrupt acknowledgements and timer enable/disable, `bnx2x_sp.c` LLH CAM programming, `bnx2x_stats.c` MAC/NIG statistics reads, and `bnx2x_self_test.c` register self-test tables.

## Control Flow

There is no runtime control flow in the header. Runtime behavior is created when other driver files combine these constants with MMIO helpers.

The common access pattern is:

1. Initialization code selects a device path, port, function, or hardware generation.
2. It writes setup values through `REG_WR()`/DMAE helpers using offsets from this file.
3. It polls read-only or read-clear status registers such as init-done, FIFO-empty, interrupt status, parity status, or write-done bits.
4. It enables or masks interrupt/attention routing through MISC/AEU, block `*_INT_MASK`, block `*_PRTY_MASK`, HC/IGU, and NIG registers.
5. Data-plane operation proceeds through hardware blocks configured by these writes, while diagnostic paths later read counters, memory windows, and error-detail registers.

Several hardware flows are implied by the register comments:

- BRB1 buffer setup must program free-list/parser credit state in a strict order after reset.
- ATC initialization requires writing the init array register and waiting for `ATC_REG_ATC_INIT_DONE`.
- DMAE commands are staged in `DMAE_REG_CMD_MEM` and triggered through `DMAE_REG_GO_C*` registers.
- IGU/HC interrupt delivery uses command registers, mapping memory, status-block producer/consumer memory, MSI/MSI-X enable state, and attention/PBA/write-done tracking.
- PGLUE/PXP/PXP2 PCIe flows capture request/completion errors and require explicit clear writes for dirty/latched error registers before new first-error detail can be logged.
- Parser/connection-manager flows depend on programmed event IDs, CM headers, physical queue numbers, context region sizes, and XX-protection credit/table limits.
- QM scheduling depends on queue-to-VOQ, VOQ-to-physical-queue, credit, WRR, and PF-enable tables being coherent with firmware and storm context setup.

## State and Persistence Behavior

- The macros describe persistent device hardware state, not kernel memory state. Writes persist in MMIO registers until reset, function reset, block reset, management firmware action, or later driver writes.
- Many registers are clear-on-read or statistics clear-on-read. Reading `RC` and `ST` registers can mutate device state and should not be treated as passive observation.
- Wide-bus registers and register-backed memories require consecutive 32-bit accesses or array-style walks. Size macros are part of the persistence contract because walking too far can hit undefined hardware space.
- Several registers reflect latched first-error state. PGLUE error detail registers, AEU latch registers, and parity status registers preserve the first/current fault until read-clear or write-clear actions are taken.
- Some control registers have write-only or write-1-to-clear semantics. Examples include latch clear paths and dirty-bit clear registers; readback may return zero or unrelated state.
- Queue, context, credit, and classifier registers encode hardware-owned operational state. Incorrect writes can persistently change packet routing, scheduling fairness, interrupt delivery, VF permissions, or DMA behavior until reinitialized.
- The header also exposes strap/override state (`MISC_REG_PORT4MODE_EN`, path-swap overrides, XMAC port mode, reset registers). These must be treated as board and reset-domain state rather than ordinary per-interface settings.

## Dependencies and Integration Points

- `bnx2x.h` includes this header, making the register namespace globally available to the driver implementation.
- MMIO helpers outside this chunk translate these offsets into PCI BAR/GRC accesses. The header assumes callers know whether an offset is global, path-local, port-local, function-local, a block-relative offset, or an array base.
- Initialization and recovery code in `bnx2x_init.h` uses parity/attention masks, AEU routing registers, and PB/GRC base combinations to set up block error reporting.
- Ethtool diagnostics in `bnx2x_ethtool.c` use this chunk directly for register read/write tests, NVM access through MCPR registers, parity status reports, and memory-dump tables.
- Self-test code uses PXP2 and related register offsets to validate register availability and expected values across hardware revisions.
- Interrupt paths use HC/IGU definitions from this chunk plus later IGU command/address constants from the rest of the header.
- Slowpath/filter code uses NIG LLH function memory and enable registers to program MAC/VLAN classification and route packets to the correct function or BRB path.
- Statistics paths use MSTAT, NIG, EMAC/BMAC, and other register windows to collect hardware counters. Some counters in this chunk are clear-on-read, so diagnostics must coordinate with normal stats collection.
- Firmware and management-controller integration uses MCP scratch/NVM/access-lock registers and MISC shared-memory address definitions to communicate with MCP firmware.

## Risks and Edge Cases

- This header is a single source of truth for raw device offsets. A wrong constant can make the driver write the wrong hardware block, which can disable DMA, break packet routing, mask real parity faults, or trigger PCIe errors.
- Access semantics matter. Treating `RC`, `ST`, `W`, `WR`, or `WB` registers as ordinary read/write registers can lose interrupt evidence, clear counters, or perform unintended actions.
- Comments identify sequencing-sensitive hardware. `BRB1_REG_FREE_LIST_PRS_CRDT` explicitly warns that invalid post-reset RBC access ordering can hang the device.
- Many arrays are sparse or hardware-generation dependent. The chunk includes legacy and newer NIG parity locations, `_EXT_A` queue-manager ranges, E1/E1H/E2/E3-era comments, and some repeated or duplicate macro names. Callers must gate programming by device generation and mode.
- Virtualization registers are security-sensitive. PGLUE VF GRC-space, length-violation, FID-enable, BME, FLR, and SR-IOV dirty-bit registers are part of PF/VF isolation and reset handling.
- Attention and parity masking can hide fatal hardware faults. Mask defaults and recovery writes need to be audited against actual ASIC errata and firmware expectations.
- Several register comments specify maximum credit values or required startup values. Exceeding those values can deadlock or starve internal pipelines.
- Port/path/function indexing is often encoded by adjacent offsets or `_0`/`_1` suffixes. Reusing a port-0 offset for port 1, or using a function output enable register for the wrong PF, can misroute interrupts or traffic.
- Some diagnostic reads have side effects. Register self-tests and ethtool dumps must avoid destructive reads during normal traffic unless the driver already expects counters/status to be cleared.
- The chunk ends in the middle of the TM family, so timer-manager analysis is incomplete here.

## Test Signals

- Compile the `bnx2x` driver with this header included. Build success catches missing/renamed macros but does not validate numeric correctness.
- Boot/probe on supported Broadcom/QLogic Everest hardware and confirm initialization reaches link setup without parity/attention storms, MMIO timeouts, or PCIe completion errors.
- Exercise interrupt modes: legacy HC, IGU, MSI, and MSI-X where supported. Useful signals are correct status-block updates, interrupt acknowledgements, attention delivery, and no stuck write-done/pending bits.
- Run ethtool register tests and dumps that touch `BRB1_REG_*`, `DORQ_REG_*`, `HC_REG_*`, `PXP2_REG_*`, `QM_REG_*`, `TM_REG_*`, `SRC_REG_*`, and NIG/LLH registers. Expected results are masked read/write matches and no destructive side effects beyond intended test windows.
- Validate NVM read/write paths through `MCP_REG_MCPR_NVM_*` with arbitration. Signals include proper arbiter acquisition/release, command completion, and no MCP access-lock contention.
- Trigger or inject parity/error conditions where a lab setup permits it. The expected path is block `*_PRTY_STS` observation, AEU after-invert bit propagation, correct masking/clearing, and recovery behavior without silent loss of error state.
- Exercise SR-IOV/virtualization flows. Confirm VF doorbells, inbound interrupt tables, PGLUE VF permission checks, FLR dirty-bit handling, and PF/VF isolation behave correctly.
- Test flow-control modes: pause, LLFC, PFC, ETS/WFQ, and multi-COS queueing. The hardware signals are BRB/PBF/NIG/QM thresholds, pause state, credit counters, and absence of queue starvation or packet drops under load.
- Exercise LLH MAC/VLAN classification and multicast hash programming. Expected signals include correct `NIG_REG_LLH*` memory programming, traffic delivery to the intended function, and correct fallback/no-match behavior.
- Run link bring-up and statistics collection across port modes. Check that clear-on-read and statistics registers do not interfere with periodic stats or diagnostic dumps.

## Chunk Notes for Merge Lane

This is the first chunk for `sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_reg.h`. It establishes the register-address vocabulary used by the rest of the `bnx2x` driver and covers many central datapath, interrupt, PCIe, and management blocks, but it is not a complete file report. The final per-file document should merge this with later chunks that define BAR/GRC base constants, AEU input bits, MDIO/PHY constants, IGU command encodings, additional PXP2/QM/NIG late additions, and the remaining header guard.

### subset-b-004369: lines 4703-7778

# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_reg.h lines 4703-7778

## Scope

This chunk is the final large register-definition slice of `bnx2x_reg.h`. It covers timer, SDM, SEM, CM, MAC, PCIe, attention, MDIO/PHY, IGU, CDU, idle-check, and CRC helper definitions used by the Broadcom NetXtreme II `bnx2x` Ethernet driver. Most content is preprocessor constants for memory-mapped GRC registers, MAC subregister offsets, MDIO Clause 22/45 registers, bit masks, queue/window ranges, and hardware attention bits. The only executable code in this chunk is the inline CRC-8 helper at the end.

The chunk does not define driver structs or high-level Linux APIs. Its API surface is the symbol namespace consumed by `bnx2x_main.c`, `bnx2x_link.c`, `bnx2x_cmn.c`, `bnx2x_sriov.c`, `bnx2x_self_test.c`, and related init/header code.

## Register And Constant Families

- Lines 4703-4733: `TM_REG_*` timer block registers for linear timer address programming, scan timeout, context region, timer tick sizing, interrupt status/mask, and parity status/mask/clear.
- Lines 4734-4815, 5216-5307, and 5767-5860: `TSDM_REG_*`, `USDM_REG_*`, and `XSDM_REG_*` SDM blocks. These publish aggregate interrupt event/T/mode slots, completion and queue counter RAM start addresses, PXP credit, enable gates, parser/PXP FIFO-empty signals, timer ticks, statistics counters, interrupt registers, and parity registers.
- Lines 4816-4950, 5308-5442, and 5861-5996: `TSEM_REG_*`, `USEM_REG_*`, and `XSEM_REG_*` SEM micro-engine registers. These cover thread arbitration elements, time-slot schemes, FIC/passive-buffer disables, fast memory, PRAM/passive-buffer memory windows, sleeping/free thread state, message counters, interrupt/parity registers, and VF/PF error reset selectors.
- Lines 4951-5189 and 5446-5727 plus 5763-5766: `UCM_REG_*` and `XCM_REG_*` connection-manager registers. They define AG context indirect windows, CDU/STORM/TM/QM/NIG/PBF/SEM/DORQ/SDM interface enables, WRR weights, initial credits, event IDs and CM headers, STORM context load sizes, physical queue mapping, message length mismatch latches, AG context region sizing, queue/counter decision registers, and XX protection CAM/table/descriptor state.
- Lines 5190-5215 and 5728-5762: UMAC/XMAC register offsets and bits for enable/reset, loopback, flow-control pause/PFC, source MAC address, EEE timers/control, maximum frame size, and link-fault status clear/masking.
- Lines 5997-6009: MCP/NVM bit definitions for access locking, NVM read/write enable, address, command sequencing, done/doit/first/last/write bits, flash size, and software arbitration.
- Lines 6010-6104: BIGMAC/BIGMAC2 and EMAC register offsets/bits for RX/TX control, max sizes, pause/PFC, MDIO command/mode/status, LED overrides, port mode, half duplex, resets, statistics counters, MTU jumbo enable, promiscuous mode, VLAN preservation, and flow control.
- Lines 6105-6200: MISC GPIO/SPIO, reset-register, and hardware-lock constants. These map board pins, output/floating modes, interrupt set/clear positions, reset bits for core blocks/MACs/PHY muxes, and shared firmware lock resource IDs.
- Lines 6201-6326: AEU attention-bit maps, reserved/general attention assignments, storm/MCP fatal assertion bits, link-sync attention bits, latched GRC/MCP parity attention bits, and `GENERAL_ATTEN_WORD()` / `GENERAL_ATTEN_OFFSET()` helpers.
- Lines 6327-6377: `GRCBASE_*` base addresses for the major device blocks, used with generated register offsets and by firmware/chipsim-compatible address calculations.
- Lines 6380-6555: PCI configuration offsets, command/status/capability bit masks, MSI/MSI-X fields, BAR/GRC access windows, BAR size encoding, power-management state bits, VF MSI-X/PF-VF assignment config, and BAR internal-memory offsets for storm memories, IGU, doorbells, and ME registers.
- Lines 6556-6803: PXPCS transaction-layer PCIe error/status bits for functions 0/1 and 2-7, duplicated BAR offsets, and ME PF/VF identity fields.
- Lines 6804-6823: VF-visible PXP address windows for IGU, USDM queues, CSDM global registers, and doorbells.
- Lines 6825-7524: MDIO/PHY register banks and bit definitions for CL73/CL37 autonegotiation, RX/TX lane equalization and drivers, XGXS lane swap/unicore modes, GP link/speed status, parallel detect, SerDes digital controls/status, over-1G user pages, BAM next pages, combo IEEE MII control/status/advertisement, PMA/PCS/AN/WIS/XS device addresses, SFP two-wire access, BCM8726/8727/8073/7101/8481/84823/84833/84858 PHY-specific control registers, PHY mailbox commands/statuses, Warpcore Clause 45 registers, CL72/CL82/KR/KR2/FEC/TX FIR controls, GPHY 54618SE IDs, interrupts, EEE, expansion, shadow LED/autodetect registers.
- Lines 7526-7624: IGU command-address space, command register offsets, MSI-X/PBA ranges, interrupt-ack and producer-update ranges, attention command slots, PF/VF configuration bits, doorbell/status-block segment counts, FID encoding, and mapping-memory field masks.
- Lines 7626-7642: CDU context-region constants and macros for computing context validation bytes from CID/region/type via CRC-8.
- Lines 7644-7718: idle-check register list for PXP/PXP2 errors, PBF task/credit counters, QM byte/VOQ credits and queue mapping, GRC timeout FID, and NIG ingress/egress FIFO-empty signals.
- Lines 7720-7778: `calc_crc8()`, an inline Verilog-derived CRC-8 implementation for polynomial bits 0-1-2-8.

## Important API Surface

The exported surface is the macro namespace itself:

- `*_REG_*` address constants are passed to `REG_RD()`, `REG_WR()`, `REG_RD8()`, and `REG_WR8()` for GRC/MMIO register access.
- `MDIO_*` constants are passed to `bnx2x_cl22_read/write()`, `bnx2x_cl45_read/write()`, and related helpers in `bnx2x_link.c` for internal Warpcore and external PHY programming.
- `*_MASK`, `*_SHIFT`, and single-bit constants encode fields for read-modify-write sequences. Several constants are pre-shifted masks, so callers should not assume all values are raw enums.
- `IGU_PF_CONF_*`, `IGU_VF_CONF_*`, `IGU_CMD_*`, `IGU_ADDR_*`, and `IGU_REG_MAPPING_MEMORY_*` are the interrupt-generation-unit ABI used during interrupt enable/disable, VF producer updates, attention signaling, and status-block mapping.
- `AEU_INPUTS_ATTN_BITS_*`, reserved attention bits, and `GENERAL_ATTEN_OFFSET()` provide the attention/parity classification contract used by the driver's interrupt, error, and recovery paths.
- `CDU_VALID_DATA()`, `CDU_CRC8()`, `CDU_RSRVD_VALUE_TYPE_A()`, `CDU_RSRVD_VALUE_TYPE_B()`, and `CDU_RSRVD_INVALIDATE_CONTEXT_VALUE()` define the context validation byte format for CDU-managed connection contexts.
- `calc_crc8(u32 data, u8 crc)` is the only function in this chunk. It splits a 32-bit data word and 8-bit seed into bit arrays, applies the hard-coded CRC-8 XOR network, and returns the recomposed 8-bit result.

High-value constants with visible consumers include `IGU_PF_CONF_FUNC_EN`, `IGU_PF_CONF_MSI_MSIX_EN`, `IGU_PF_CONF_INT_LINE_EN`, `IGU_PF_CONF_ATTN_BIT_EN`, `IGU_PF_CONF_SINGLE_ISR_EN`, `CDU_REGION_NUMBER_UCM_AG`, `CDU_REGION_NUMBER_XCM_AG`, `MDIO_WC_REG_*` Warpcore registers, `MDIO_848xx_CMD_HDLR_*` mailbox registers, `PHY848xx_CMD_*`, `PHY84833_STATUS_*`, `PHY84858_STATUS_*`, `PXP_REG_HST_VF_DISABLED_ERROR_*`, `PBF_REG_DISABLE_NEW_TASK_PROC_Q*`, and the NIG FIFO-empty registers.

## Control Flow And Runtime Use

This header has almost no local control flow; it describes hardware state and access protocols. Runtime flow is distributed through the driver:

1. Initialization and reset paths select a block, calculate a GRC address from these constants, and write enable, credit, mask, parity, or reset values.
2. Interrupt setup in `bnx2x_main.c` reads `IGU_REG_PF_CONFIGURATION`, updates `IGU_PF_CONF_*` bits depending on MSI-X/MSI/INTx mode, acknowledges stale status when needed, and finally sets `IGU_PF_CONF_FUNC_EN`.
3. Interrupt disable clears `IGU_PF_CONF_MSI_MSIX_EN`, `IGU_PF_CONF_INT_LINE_EN`, and `IGU_PF_CONF_ATTN_BIT_EN`; older E1 paths use HC-specific masking while later chips use IGU config directly.
4. Attention/parity handlers classify asserted bits using `AEU_INPUTS_ATTN_BITS_*` and `GENERAL_ATTEN_OFFSET()`-derived masks, then route to block-specific logging, recovery, or fatal paths.
5. Link setup in `bnx2x_link.c` sequences MDIO writes using the MDIO constants. Warpcore AN/KR/KR2/XFI/SFI/SGMII code writes CL73/CL72/BAM, TX FIR/driver, lane control, 64/66, and GP status registers; status reads use GP/link/speed fields to set `link_vars`.
6. External PHY flows use the BCM848xx mailbox definitions by polling status, writing up to five data registers, writing a command, polling for pass/error, and reading result registers.
7. Context initialization in `bnx2x_cmn.c` calls `CDU_RSRVD_VALUE_TYPE_A(HW_CID(...), CDU_REGION_NUMBER_UCM_AG/XCM_AG, ETH_CONNECTION_TYPE)` to stamp USTORM/XSTORM contexts with validation bytes derived by `calc_crc8()`.
8. SR-IOV paths use IGU command ranges such as `IGU_CMD_E2_PROD_UPD_BASE + igu_sb_id` to build VF producer-update addresses.
9. Self-test/idle-check tables reference the idle-check register constants to verify PXP, PBF, QM, and NIG quiescence or error state.

## State And Persistence Behavior

The header itself is stateless. The state it names is persistent hardware state across many calls and sometimes across function-level reset boundaries until explicitly cleared or reinitialized.

State-sensitive areas include:

- Timer/SDM/SEM/CM registers hold interrupt, parity, queue, credit, context, arbitration, and FIFO state. Some status registers are read-clear (`RC`), so reads can acknowledge or destroy diagnostic evidence.
- Interface-enable and credit registers gate traffic between internal blocks. Wrong values can stall command, completion, timer, storm, or queue-manager traffic.
- SEM free/sleeping-thread lists, FIC/PAS disables, PRAM, fast memory, passive-buffer memory, and interrupt tables represent microcode engine runtime state and should not be treated as ordinary scratch registers.
- MAC registers hold link-facing state such as TX/RX enable, reset, max frame size, source MAC for pause/PFC frames, EEE behavior, pause/PFC enables, and link-fault status.
- MCP/NVM lock and command bits coordinate access to firmware/NVRAM resources. The hardware-lock constants define shared ownership between driver, management firmware, and other functions.
- PCIe/PXPCS status bits are often write-clear or read-only diagnostics. Misclassification can hide fatal PCIe conditions or cause noisy attention handling.
- MDIO/PHY registers persist link mode, advertised capabilities, lane polarity/swap, equalization, firmware mode, EEE, SFP two-wire access state, and PHY mailbox status.
- IGU configuration controls whether a PF/VF can generate interrupts, whether MSI-X/MSI/INTx is active, which parent PF a VF maps to, and how mapping-memory entries encode vector/FID ownership.
- CDU validation bytes persist in connection contexts and are consumed by hardware context validation.

## Dependencies And Integration Points

- `bnx2x_main.c`: consumes IGU PF configuration, AEU attention bits, XCM masks, BAR/IGU command offsets, reset/MISC constants, and block bases during load/unload, interrupt mode transitions, parity handling, and recovery.
- `bnx2x_link.c`: the dominant consumer of MDIO/PHY, MAC, NIG/PBF, MCP/NVM, GPIO/SPIO, and Warpcore constants. It programs autonegotiation, forced speeds, PHY firmware modes, EEE, SFP/two-wire access, lane reset/polarity, and LED/media behavior.
- `bnx2x_cmn.c`: uses CDU region and CRC macros in `bnx2x_set_ctx_validation()` to stamp connection contexts.
- `bnx2x_sriov.c`: uses IGU command producer-update ranges for VF status-block producer writes.
- `bnx2x_self_test.c`: uses idle-check registers to define hardware health/quiescence probes.
- `bnx2x.h` and `bnx2x_init.h`: compose attention/parity masks from `AEU_INPUTS_ATTN_BITS_*` and `GENERAL_ATTEN_OFFSET()` definitions.
- Firmware and hardware specifications: many comments mention generated design names and internal blocks, making these constants a contract with device RTL/firmware rather than normal driver-local policy.

## Risks And Edge Cases

- Address or bit drift is high impact. A wrong constant can write to the wrong hardware block, corrupt link setup, mask a parity event, break MSI-X/MSI/INTx routing, or stall an internal queue.
- Several registers are read-clear or write-clear. Diagnostic code must not casually read `*_STS_CLR`, length-mismatch, parity, PCIe error, or mailbox status registers unless it intends to acknowledge them.
- Constants mix raw values, shifted masks, and encoded values. For example, many MDIO/PCI/IGU fields are already shifted; double-shifting or using a mask as a value can corrupt neighboring bits.
- Link programming is tightly sequenced. Warpcore setup frequently changes AER lane selection, disables AN, writes global and lane-specific registers, restores AER, resets lanes, and then restarts AN. Reordering register writes can leave a lane stuck or report false link.
- Shared-resource locks matter. NVM, MDIO, GPIO/SPIO, reset, and DCBX/admin resources are coordinated through hardware-lock IDs; bypassing these risks races with firmware or another PF.
- `CDU_RSRVD_VALUE_TYPE_B(_crc, _type)` appears malformed in this chunk because it references `_cid` and `_region` inside the body despite not accepting those parameters. It appears unused in the local `bnx2x` tree, but using it as written would not compile.
- `calc_crc8()` comment says it splits data into 31 bits, but the loop processes 32 bits. The implementation, not the comment, is what CDU validation depends on.
- Some PHY definitions are vendor/model-specific. Applying BCM84833/84858 mailbox statuses, BCM84823 media straps, 54618SE GPHY shadows, or Warpcore registers to the wrong PHY path can hang polling loops or misconfigure media.
- Duplicate BAR constants appear in this chunk. They match earlier definitions here, but future edits should avoid creating divergent duplicate values.
- Idle-check constants are hardware-generation sensitive. Some NIG/PBF/QM empty signals or queue IDs may only be valid on specific chip revisions or traffic modes.

## Test And Validation Signals

- Build signal: `bnx2x` must compile with all consumers of these symbols. Any changed macro name, invalid macro body, or missing address constant will usually fail at compile time.
- Interrupt-mode smoke: load/unload the driver with MSI-X, MSI, and INTx where supported; verify `IGU_REG_PF_CONFIGURATION` updates do not leave interrupts disabled, duplicated, or stuck.
- Link bring-up: validate autoneg and forced modes across supported media, especially KR/KR2/XFI/SFI/SGMII paths that use `MDIO_WC_REG_*` sequencing. Useful observations are link-up, negotiated speed/duplex, pause/FEC/EEE negotiation, and no repeated link recovery.
- PHY mailbox: for BCM84833/84858, exercise pair-swap and EEE mailbox commands and verify pass/error/timeout handling around `MDIO_848xx_CMD_HDLR_*` and `PHY848xx_*` statuses.
- Context validation: exercise L2 connection setup and teardown so `bnx2x_set_ctx_validation()` stamps USTORM/XSTORM contexts; hardware should accept contexts without CDU validation faults.
- Attention/parity handling: inject or observe AEU attention/parity conditions if supported by test hardware; verify the asserted bits map to the expected block names and recovery behavior.
- SR-IOV: verify VF producer updates, interrupt delivery, and parent PF/FID mapping with VFs enabled.
- Idle check: run the driver's self-test/idle-check path after quiescing traffic and confirm PXP/PBF/QM/NIG checks using this chunk's registers pass or produce meaningful failures.

## Chunk Notes For Merge Lane

This chunk is the tail of `bnx2x_reg.h` and includes both generated-style hardware register definitions and the file-closing `calc_crc8()` helper. The final per-file report should treat `bnx2x_reg.h` as a hardware register contract consumed throughout the driver, not as standalone driver logic. Earlier chunks are needed for the rest of the block register map; this chunk contributes the key link/PHY, interrupt/attention, IGU/CDU, idle-check, and CRC-validation portions.
