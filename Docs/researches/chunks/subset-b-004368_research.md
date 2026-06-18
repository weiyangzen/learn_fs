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
