# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_regs.h

## Purpose

`t4_regs.h` defines the memory-mapped register address map and bitfield helpers for Chelsio T4/T5/T6 adapters. It is the driver’s primary register ABI reference, covering PF/port address helpers, SGE queues and interrupts, PCIe, memory controllers, CIM/mailboxes, TP offload engine, PM/ULP datapaths, MPS/MAC statistics and tracing, RSS/filter/LE database control, serial flash, PL top-level interrupts, NCSI/SMB, and T5/T6-specific register deltas.

## Important APIs, Types, and Constants

- Address helpers: `MYPF_REG`, `PF_REG`, `MYPORT_REG`, `PORT_REG`, `EDC_REG`, `PCIE_MEM_ACCESS_REG`, `PCIE_MAILBOX_REG`, `MC_BIST_STATUS_REG`, `EDC_BIST_STATUS_REG`, `PCIE_FW_REG`, `T5_PORT_REG`, `MC_REG`, and `EDC_T5_REG`.
- SGE block: PF/VF doorbells, GTS, control registers, context command/data, host page size, queues-per-page, interrupt cause/enable registers, free-list buffers, ingress thresholds, congestion-manager control, timestamp, DBFIFO/DBVFIFO status, doorbell control, timer values, debug data, error stats, and DBQ context base. Bitfields cover QID/PIDX/CIDX, boundaries, VFIFO, context type/QID, per-PF page sizes, queue errors, dropped doorbells, HP/LP FIFO thresholds/counts, stat modes, and T5/T6 differences.
- PCIe block: PF config/CLI/expansion ROM offset, interrupt cause and nonfatal error fields, configuration-space access registers, memory access base/offset windows, firmware registers, core status registers, and static spare configuration version.
- Memory blocks: MC/MC_P ECC status, interrupt cause, BIST command/address/length/pattern/status; MA EDRAM/external-memory BARs, target memory enable, wrap/parity status; EDC base/stride, BIST, ECC and parity status.
- CIM block: boot/SDRAM/extmem configuration, PF mailbox data/control/shadow, mailbox ownership/valid/interrupt bits, host interrupt cause/enable, host upper-access errors, host access control/data, IBQ/OBQ debug configuration/data, queue configuration, logic analyzer/debug pointers, and queue address/counter fields.
- TP block: debug logic analyzer, global/output config, CMM/PMM base and max-page registers, timer resolution, retransmit/persist/keepalive/delayed-ack timers, shift counts, congestion-control/pace/MTU/RSS lookup tables, PIO/MIB access, FLM free counts, offload/tunnel rates, VLAN priority map/filter tuple selection, ingress checksum/VNIC config, RSS config/key/VF/PF maps, and TX scheduler/modulation registers.
- ULP/PM blocks: ULP TX interrupt and table limit registers, TX logic analyzer/debug registers, PM RX/TX interrupt/stat/debug registers, framing and parity error bits, ULP RX limits for iSCSI/TDDP/STAG/RQ/PBL/TLS key memory, and ULP RX logic analyzer registers.
- MPS/MAC blocks: per-port TX/RX/loopback statistics, magic MAC and PTP timestamp/sum registers, MAC/XGMAC EPIO access, common/stat/interrupt controls, TX/RX FIFO parity, background drop/truncate stats, trace configuration/RSS/filter controls, classifier TCAM/SRAM data/control, VF replication maps, VXLAN/GENEVE UDP type configuration, and T5/T6 MPS classifier sizing.
- LE/CPL/PL/SF/NCSI/SMB blocks: CPL interrupt cause, SMB/NCSI parity interrupts, serial flash data/op and busy/lock/cont/byte/op bits, PF/top-level PL interrupts/enables/reset/revision/whoami, LE database config/hash/table/index/count/interrupt/response code registers, and T6 LE hash mask registers.

## Control Flow and State Behavior

This header has no executable control flow. It drives control flow in hardware access routines that compute register addresses, poll busy bits, read interrupt causes, write enables, configure queues, and decode status registers. Common usage patterns implied by the constants include:

- Queue setup writes SGE control, page-size, free-list buffer, context, and doorbell registers, then uses GTS/doorbell fields for runtime producer/consumer updates.
- Interrupt handlers read module-level and top-level cause registers, mask individual bits, clear handled causes, and may query error status registers for queue IDs or ECC counts.
- Firmware/mailbox code uses CIM PF mailbox data/control registers and mailbox owner/valid/interrupt fields to arbitrate between driver and firmware.
- Memory diagnostics use MC/EDC BIST command/status and ECC/parity counters.
- RSS/filter/offload configuration writes TP RSS, VLAN priority map, LE database, and MPS classifier registers.
- Debug and ethtool paths use logic analyzer, MIB/stat, trace, TCAM/SRAM, and queue debug registers.

The persistent state is entirely in hardware registers, adapter memory, EEPROM/flash-related access paths, or firmware-owned tables. The header names locations and bit meanings but does not itself persist state. Register writes made by callers may survive until reset, firmware reload, or explicit reconfiguration, depending on the hardware block.

## Dependencies and Integration Points

- No explicit includes; it is pure preprocessor definitions.
- Integrated by low-level adapter code that performs MMIO register reads/writes, interrupt setup, firmware communication, diagnostics, statistics collection, RSS/filter setup, and hardware bring-up/reset.
- Complements `t4_values.h`, which supplies modal values for some fields defined here, and `t4_hw.h`, which supplies global dimensions used to iterate register instances.
- Works with `t4_msg.h` and `t4_tcb.h` indirectly: register programming enables queues and offload engines that exchange CPL messages and manipulate TCB state.
- Address helpers encode PF/port/generation layout assumptions, so they are central integration points for SR-IOV, PF-specific mailbox, port-stat, and T5/T6 access paths.

## Risks and Edge Cases

- Register offsets and bit positions are strict hardware ABI. A wrong value can disable queues, break interrupts, corrupt adapter memory, or misdiagnose fatal errors.
- Many `_V(x)` macros do not mask input before shifting. Callers must validate field widths using the corresponding `_M` values where provided.
- Some names are deliberately repeated for registers/bits reused in multiple contexts, such as `SGE_DOORBELL_CONTROL_A`, `SGE_CTXT_CMD_A`, `ENABLE_DROP_*`, `HP_INT_THRESH_*`, and `DATALKPTYPE_*`. This is legal in C only when definitions match; future edits must avoid incompatible redefinitions.
- T5/T6 variants have different shifts, widths, base addresses, port strides, classifier sizes, and source-PF encodings. Incorrect generation checks in callers are high risk.
- Several registers are indexed or strided; callers must bound indices against instance-count constants such as `NUM_LE_DB_DBGI_REQ_DATA_INSTANCES`, `NUM_MPS_CLS_TCAM_Y_L_INSTANCES`, `NUM_MPS_CLS_SRAM_L_INSTANCES`, and T5/T6 variants.
- Busy bits such as SGE context busy, LE DB debug busy, SF busy, CIM host busy, and IBQ/OBQ debug busy require timeout handling in callers to avoid hangs on faulty hardware.
- Top-level interrupt bits aggregate submodule failures; handlers must read the subordinate cause registers before clearing or masking to avoid losing diagnostic information.

## Test Signals

- Full driver build catches duplicate macro mismatches and missing definitions.
- Adapter bring-up on T4/T5/T6 validates PF/port base helpers, SGE setup, mailbox ownership, and PL interrupt routing.
- TX/RX traffic with interrupts and NAPI validates doorbell/GTS, queue status, SGE timers, and error paths.
- ethtool statistics and diagnostics validate MPS/MAC/TP MIB offsets, PM/ULP counters, and debug register reads.
- Firmware flash/mailbox operations validate CIM mailbox and serial flash register sequences.
- Fault-injection or hardware error tests should verify ECC/parity/interrupt bits and queue error reporting.
- RSS/filter/tunnel tests validate TP RSS, LE DB, MPS classifier, VXLAN, and GENEVE register programming.
