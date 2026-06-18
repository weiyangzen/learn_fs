# subset-b-000970 Research

This grouped report covers eight Gaudi NIC QMAN register-map headers. Each file is an auto-generated GPL-2.0 C header that exports preprocessor constants only; there are no functions, structs, enums, or inline helpers in these files. All eight headers have the same 406-register layout and differ by NIC/QM instance name plus MMIO address window.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic1_qm0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic1_qm0_regs.h

## Purpose

`nic1_qm0_regs.h` defines the memory-mapped register offsets for the Gaudi `NIC1_QM0` QMAN block. It is included through `gaudi_regs.h` and gives driver code stable names for queue-manager control, doorbell, status, command-processor, arbitration, rate-limit, indirect-gateway, and error registers. The local register window starts at `mmNIC1_QM0_GLBL_CFG0` offset `0xD20000` and runs through `mmNIC1_QM0_GLBL_MEM_INIT_BUSY` offset `0xD20D00`; `gaudi_blocks.h` maps the block base as `mmNIC1_QM0_BASE 0x7FFCD20000ull`, with section size `0x2000` and max offset `0xD040`.

## Important APIs, Types, and Macros

This header exports macros only. Important families are:

- `GLBL_*`: global configuration, protection, secure and non-secure AXI properties, status, message enable, error address/data, and memory initialization state.
- `PQ_*`: four producer queues, including base low/high, size, producer index, consumer index, configuration, ARUSER properties, and status registers.
- `CQ_*`: five completion queues, including configuration, ARUSER properties, status, pointer, transfer size, control, latched pointer/status, and IFIFO counters.
- `CP_*`: five command processors, with message base address banks, LDMA offsets, fence read data and counters, command-processor status, current instruction address, barrier config, debug, ARUSER, and AWUSER registers.
- `ARB_*`: scheduler/arbitration controls, WRR weights, master credit controls, 32 choice queue offsets, slave/master routing, message attributes, state/status, error cause/message enable/drop status, and 32 master credit status registers.
- `CGM_*`, `CSMR_STRICT_PRIO_CFG`, `HBW_RD_RATE_LIM_CFG_*`, `LBW_WR_RATE_LIM_CFG_*`, `LOCAL_RANGE_*`, `GLBL_AXCACHE`, and `IND_GW_APB_*`: clock-gating/status, priority/rate limiting, local address range, AXI cache attribute, and indirect APB gateway registers.

## Control Flow and Integration

The header has no executable control flow. Runtime behavior comes from code that uses these constants with MMIO helpers such as `WREG32` and device-specific helpers. In `gaudi.c`, `mmNIC1_QM0_GLBL_CFG1` is written during NIC QMAN stop/stall handling when `HW_CAP_NIC2` is initialized; the driver reuses `NIC0_QM0_GLBL_CFG1_*_STOP_MASK` bit definitions because the QMAN layout is shared. Queue submission maps `GAUDI_QUEUE_ID_NIC_2_0...GAUDI_QUEUE_ID_NIC_2_3` to doorbells by adding a 4-byte queue offset to `mmNIC1_QM0_PQ_PI_0`. Interrupt handling maps `GAUDI_EVENT_NIC1_QM0` to `mmNIC1_QM0_BASE` and the `NIC1_QM0` description before calling QMAN error handling. `gaudi_security.c` uses the same register constants to build protected-register masks and to expose only selected QMAN registers.

## State and Persistence Behavior

The header itself stores no software state. The named registers describe volatile device state that persists in hardware until reset, firmware reinitialization, or explicit driver writes. State-bearing groups include PQ producer/consumer indexes, CQ pointers and latched pointer status, CP current instruction/fence counters, arbitration credits, error cause/drop/status registers, and memory-init busy. Writes to configuration, queue base, queue size, security property, AR/AWUSER, rate-limit, and arbitration registers change live device behavior.

## Dependencies

The file depends only on the C preprocessor and include guards. It is pulled into the Gaudi driver via `include/gaudi/asic_reg/gaudi_regs.h`. Full block base and section metadata live in `gaudi_blocks.h`; bit masks for the shared QMAN layout are mostly represented by `nic0_qm0_masks.h`. Consumers depend on queue IDs, hardware capability bits, async event IDs, and MMIO helpers in the Gaudi driver.

## Risks

The file is auto-generated and should not be edited by hand. Any wrong offset can redirect MMIO reads/writes into another hardware block, which is especially risky for queue doorbells, security property registers, and error registers. The spelling `CHOISE` appears in generated macro names and is part of the ABI of these headers; correcting it locally would break consumers. Because this instance is tied to `HW_CAP_NIC2` and queue IDs for NIC 2 traffic, mismatched NIC numbering in call sites is a realistic integration risk.

## Test Signals

Useful signals are successful kernel build including `gaudi_regs.h`, successful NIC2 queue submission with producer-index writes landing at `mmNIC1_QM0_PQ_PI_0 + n * 4`, clean QMAN stop/stall behavior via `GLBL_CFG1`, correct `GAUDI_EVENT_NIC1_QM0` IRQ diagnostics, security mask generation that includes `GLBL_CFG1`, `GLBL_NON_SECURE_PROPS_*`, and `PQ_PI_0`, and hardware/firmware tests showing no unexpected QMAN arbitration or CP fence errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic1_qm0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic1_qm1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic1_qm1_regs.h

## Purpose

`nic1_qm1_regs.h` defines the auto-generated MMIO register offsets for the Gaudi `NIC1_QM1` QMAN block. The register layout mirrors `NIC1_QM0`, but the address window starts at `mmNIC1_QM1_GLBL_CFG0` offset `0xD22000` and ends at `mmNIC1_QM1_GLBL_MEM_INIT_BUSY` offset `0xD22D00`. `gaudi_blocks.h` defines the full block base as `mmNIC1_QM1_BASE 0x7FFCD22000ull`, with section size `0x2000` and max offset `0xD040`.

## Important APIs, Types, and Macros

This file provides 406 `#define` constants and no functions or data types. It covers the standard QMAN register families: global config/protection/status and secure/non-secure properties; four PQ rings with base, size, PI/CI, config, ARUSER, and status registers; five CQ rings with config, pointer, transfer-size, control, latched status, and IFIFO counters; five CP register groups for message bases, LDMA offsets, fences, current instruction, barriers, debug, and AXI user attributes; arbitration controls for WRR, credits, 32 choice offsets, master/slave routing, message attributes, errors, and credit status; plus CGM, local range, rate limiter, AXCACHE, indirect gateway, global error, and memory-init busy registers.

## Control Flow and Integration

There is no executable flow in the header. Driver code uses the constants as MMIO offsets. `gaudi.c` writes `mmNIC1_QM1_GLBL_CFG1` during QMAN stop/stall handling when `HW_CAP_NIC3` is initialized. Queue submission maps `GAUDI_QUEUE_ID_NIC_3_0...GAUDI_QUEUE_ID_NIC_3_3` to doorbell writes beginning at `mmNIC1_QM1_PQ_PI_0`. IRQ handling maps `GAUDI_EVENT_NIC1_QM1` to `mmNIC1_QM1_BASE` and the `NIC1_QM1` description before invoking QMAN error handling. `gaudi_security.c` references `GLBL_CFG1`, `GLBL_NON_SECURE_PROPS_*`, and `PQ_PI_0` to build protection masks for this instance.

## State and Persistence Behavior

The header is stateless, but the registers name persistent hardware state. Queue and CP progress are tracked by PQ/CQ indexes and pointers, CP current instruction registers, fence counters, and FIFO counters. Scheduling state is visible through arbitration credit/status registers. Error cause, error drop, global error address, write-data, and memory-init busy registers expose fault and initialization state. Writes persist in the live device until reset or reconfiguration.

## Dependencies

`gaudi_regs.h` includes this header for normal Gaudi builds. `gaudi_blocks.h` supplies the full base address and section metadata. Runtime users depend on Gaudi queue IDs, `HW_CAP_NIC3`, async event `GAUDI_EVENT_NIC1_QM1`, shared NIC QMAN masks, and MMIO helper macros.

## Risks

The major risks are generated-register drift and instance misbinding. A bad offset can corrupt a neighboring NIC/QMAN block or silently ring the wrong queue doorbell. Security-sensitive registers include `GLBL_PROT`, secure/non-secure property registers, AR/AWUSER fields, and the indirect APB gateway. The generated `CHOISE` spelling must remain unchanged because call sites must use the generated names.

## Test Signals

Build coverage should verify inclusion through `gaudi_regs.h`. Runtime signals include NIC3 queue submissions updating the expected `PQ_PI` register, clean QMAN stop through `GLBL_CFG1`, correct IRQ decoding for `GAUDI_EVENT_NIC1_QM1`, security masks containing this instance's non-secure property and doorbell registers, and absence of CP fence/arbitration errors during NIC3 traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic1_qm1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic2_qm0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic2_qm0_regs.h

## Purpose

`nic2_qm0_regs.h` defines the generated register offsets for Gaudi `NIC2_QM0`, one of the NIC queue-manager instances. Its local window starts at `mmNIC2_QM0_GLBL_CFG0` offset `0xD60000` and ends at `mmNIC2_QM0_GLBL_MEM_INIT_BUSY` offset `0xD60D00`. `gaudi_blocks.h` gives the full base as `mmNIC2_QM0_BASE 0x7FFCD60000ull`, section size `0x2000`, and max offset `0xD040`.

## Important APIs, Types, and Macros

The file has 406 macro definitions and no functions, types, or storage. The exported names cover global QMAN configuration and protection, secure/non-secure property programming, four producer queues, five completion queues, five command processors, arbitration/scheduling and credit accounting, CGM status, strict priority and bandwidth rate-limiter controls, local range, AXCACHE, indirect APB gateway, global error capture, and memory initialization status.

## Control Flow and Integration

The header contributes constants consumed by the Gaudi driver. In `gaudi.c`, `mmNIC2_QM0_GLBL_CFG1` is written with the shared QMAN stop masks when `HW_CAP_NIC4` is active. Queue submission maps `GAUDI_QUEUE_ID_NIC_4_0...GAUDI_QUEUE_ID_NIC_4_3` to `mmNIC2_QM0_PQ_PI_0 + q_off`, where `q_off` is the selected queue lane times four bytes. Async error handling maps `GAUDI_EVENT_NIC2_QM0` to `mmNIC2_QM0_BASE` and dispatches through the common QMAN error path. Security setup references this header's global config, non-secure property, and producer-index registers.

## State and Persistence Behavior

The macros name hardware state rather than C state. Persistent device state includes queue base/size configuration, producer and consumer indexes, completion queue pointers, command-processor message base and fence registers, arbitration credits, error causes, and memory initialization status. These registers are volatile from the CPU perspective but persist in the hardware block until reset or explicit reprogramming.

## Dependencies

The aggregate `gaudi_regs.h` includes the header. Full address metadata is in `gaudi_blocks.h`; common bit masks are shared with the NIC0 QMAN mask header. Runtime integration depends on Gaudi hardware capability `HW_CAP_NIC4`, queue ID definitions, `GAUDI_EVENT_NIC2_QM0`, and low-level MMIO read/write helpers.

## Risks

Offset correctness is critical because this file sits in a distinct NIC2 address window. Misusing `NIC2_QM0` constants for another QMAN instance can stop or ring the wrong queues. Security and isolation risks center on `GLBL_PROT`, secure/non-secure property registers, AR/AWUSER attributes, and the indirect APB gateway. Manual edits would also risk diverging from the hardware register generator.

## Test Signals

Expected signals include successful compilation, NIC4 queue doorbells resolving from `mmNIC2_QM0_PQ_PI_0`, QMAN stop/stall writes to `GLBL_CFG1`, `GAUDI_EVENT_NIC2_QM0` interrupts producing the expected block description, correct security-mask bits for the `0xD60000` window, and hardware runs without unexpected arbitration credit, CP fence, or global error reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic2_qm0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic2_qm1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic2_qm1_regs.h

## Purpose

`nic2_qm1_regs.h` provides the auto-generated MMIO offsets for the Gaudi `NIC2_QM1` QMAN block. It is the QM1 companion to `NIC2_QM0`, with the same register layout shifted to the `0xD62000` local window. The first exported register is `mmNIC2_QM1_GLBL_CFG0 0xD62000`, the last is `mmNIC2_QM1_GLBL_MEM_INIT_BUSY 0xD62D00`, and `gaudi_blocks.h` defines `mmNIC2_QM1_BASE 0x7FFCD62000ull`, section `0x2000`, max offset `0xD040`.

## Important APIs, Types, and Macros

There are no C APIs beyond preprocessor constants. The register map includes global config/protection/status, secure and non-secure global properties, PQ ring setup and doorbells for four producer queues, CQ setup/status for five completion queues, CP message and synchronization registers for five command processors, arbitration WRR/credit/routing/error registers, CGM status, CSMR strict-priority config, HBW/LBW rate-limit knobs, local range, global AXCACHE, indirect APB gateway, global error capture, and memory-init busy status.

## Control Flow and Integration

The file is consumed through `gaudi_regs.h`. `gaudi.c` writes `mmNIC2_QM1_GLBL_CFG1` during QMAN stop when `HW_CAP_NIC5` is initialized. Doorbell selection for `GAUDI_QUEUE_ID_NIC_5_0...GAUDI_QUEUE_ID_NIC_5_3` starts at `mmNIC2_QM1_PQ_PI_0`. Error handling maps `GAUDI_EVENT_NIC2_QM1` to `mmNIC2_QM1_BASE` and the `NIC2_QM1` label, then uses common QMAN diagnostics. `gaudi_security.c` uses selected offsets from this header to define non-secure access/protection masks.

## State and Persistence Behavior

The file stores no state, but it exposes device state registers. Queue progress is held in PQ/CQ producer, consumer, pointer, size, and control registers. Command processing state is represented by message base registers, LDMA offsets, fences, current instruction addresses, barrier configuration, and debug registers. Arbitration credits and error registers reflect scheduler state. Settings remain programmed in the hardware block until reset or a later driver/firmware write.

## Dependencies

Dependencies are the aggregate register include, block-base definitions in `gaudi_blocks.h`, common QMAN mask definitions, Gaudi queue and event enumerations, hardware capability flags, and the driver's MMIO helpers. The header itself needs only standard preprocessor support.

## Risks

The main risk is address-window mismatch: `NIC2_QM1` offsets are close to but distinct from `NIC2_QM0`, and using the wrong prefix affects different queues. Security-sensitive fields are the global protection/property registers and AXI user attributes. Indirect gateway and error registers are low-level hardware controls and should be treated as register-generator output, not hand-maintained source.

## Test Signals

Tests should observe successful build, NIC5 queue submission doorbells at `mmNIC2_QM1_PQ_PI_0 + lane * 4`, correct stop/stall writes to `mmNIC2_QM1_GLBL_CFG1`, IRQ handling for `GAUDI_EVENT_NIC2_QM1`, protected-register mask coverage for non-secure props and PQ PI, and clean hardware execution without CP/arbitration/global errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic2_qm1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic3_qm0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic3_qm0_regs.h

## Purpose

`nic3_qm0_regs.h` defines the generated register names and offsets for the Gaudi `NIC3_QM0` queue manager. The local address range starts at `mmNIC3_QM0_GLBL_CFG0 0xDA0000` and extends through `mmNIC3_QM0_GLBL_MEM_INIT_BUSY 0xDA0D00`. `gaudi_blocks.h` pairs this with `mmNIC3_QM0_BASE 0x7FFCDA0000ull`, section `0x2000`, max offset `0xD040`.

## Important APIs, Types, and Macros

The header exports only 406 `#define` constants. Register groups include global configuration/protection/status and message-enable controls; secure and non-secure global properties; producer queue base/size/PI/CI/config/ARUSER/status registers for four PQs; completion queue config/status/pointer/transfer/control/IFIFO registers for five CQs; command processor message-base, LDMA, fence, current-instruction, barrier, debug, ARUSER, and AWUSER registers for five CPs; arbitration WRR, credits, choice offsets, routing, state, error, and credit status registers; plus clock-gating, priority, bandwidth limit, local range, AXCACHE, APB indirect gateway, and global error/mem-init registers.

## Control Flow and Integration

No executable code is present. In the Gaudi runtime, `mmNIC3_QM0_GLBL_CFG1` is used in QMAN stop handling for `HW_CAP_NIC6`. Queue doorbells for `GAUDI_QUEUE_ID_NIC_6_0...GAUDI_QUEUE_ID_NIC_6_3` are computed from `mmNIC3_QM0_PQ_PI_0`. QMAN error handling maps `GAUDI_EVENT_NIC3_QM0` to `mmNIC3_QM0_BASE`, labels the block `NIC3_QM0`, and routes through the common QMAN error printer/handler. Security code derives protection masks from `GLBL_CFG1`, `GLBL_NON_SECURE_PROPS_*`, and `PQ_PI_0`.

## State and Persistence Behavior

The register definitions expose hardware state. Queue, completion, CP, arbitration, and error-status registers reflect live device state and are updated by both driver writes and hardware progress. Configuration writes persist until the NIC QMAN block is reset or reprogrammed. The `GLBL_MEM_INIT_BUSY` and global error registers are important for initialization and fault diagnosis.

## Dependencies

The file is included by `gaudi_regs.h`, while base address metadata comes from `gaudi_blocks.h`. Consumers rely on shared NIC QMAN masks, Gaudi queue/event IDs, `HW_CAP_NIC6`, and MMIO access helpers. There are no local include dependencies beyond the include guard.

## Risks

Incorrect offsets can affect the wrong QMAN instance or corrupt live queue state. Doorbell and queue base registers are high-risk because small arithmetic mistakes can submit work to the wrong producer queue. Security risks involve global protection, non-secure property, AR/AWUSER, and indirect-gateway registers. Since the file is generated, manual edits may be overwritten or may desynchronize from hardware documentation.

## Test Signals

Useful checks are build coverage through `gaudi_regs.h`, NIC6 queue traffic causing expected `PQ_PI` writes, correct `GLBL_CFG1` stop behavior, correct `GAUDI_EVENT_NIC3_QM0` diagnostics, protected-register masks matching the `0xDA0000` register window, and no unexpected QMAN error causes or arbitration credit exhaustion during NIC3/QM0 workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic3_qm0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic3_qm1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic3_qm1_regs.h

## Purpose

`nic3_qm1_regs.h` is the generated register-offset map for the Gaudi `NIC3_QM1` QMAN block. It mirrors the other NIC QMAN maps with instance-specific names and address constants. The first local offset is `mmNIC3_QM1_GLBL_CFG0 0xDA2000`, the last is `mmNIC3_QM1_GLBL_MEM_INIT_BUSY 0xDA2D00`, and the full block base in `gaudi_blocks.h` is `mmNIC3_QM1_BASE 0x7FFCDA2000ull`.

## Important APIs, Types, and Macros

Only macros are defined. The 406 constants cover global control and status, protection and security property registers, producer queue setup/doorbell/status for four PQs, completion queue setup/status/pointer/control for five CQs, five command-processor register groups for message bases/LDMA/fences/current instruction/barriers/debug/AXI attributes, arbitration scheduler and credit state, CGM, strict priority, bandwidth rate limits, local range, AXCACHE, indirect APB access, global error capture, and memory initialization status.

## Control Flow and Integration

The file has no branches or functions. `gaudi.c` uses `mmNIC3_QM1_GLBL_CFG1` for QMAN stop handling under `HW_CAP_NIC7`; it computes queue doorbells for `GAUDI_QUEUE_ID_NIC_7_0...GAUDI_QUEUE_ID_NIC_7_3` from `mmNIC3_QM1_PQ_PI_0`; and it maps `GAUDI_EVENT_NIC3_QM1` to `mmNIC3_QM1_BASE` for common QMAN error reporting and recovery. `gaudi_security.c` uses selected offsets from the same header for protection-bit masks.

## State and Persistence Behavior

There is no C-level persistence, but the referenced hardware registers hold persistent device configuration and live queue state. Queue ring addresses/sizes, producer indexes, completion pointers, command-processor fences and current instructions, arbitration credits, and error registers remain meaningful across driver operations until reset or reconfiguration. Some status registers are hardware-updated as work progresses.

## Dependencies

The header participates in the aggregate register namespace via `gaudi_regs.h`. Full base and section metadata come from `gaudi_blocks.h`; shared masks and bit fields come from NIC0 QMAN masks due to layout reuse. Runtime call sites depend on Gaudi queue IDs, async event IDs, `HW_CAP_NIC7`, and MMIO helpers.

## Risks

The register window is adjacent to `NIC3_QM0`, so prefix mistakes can be hard to spot but severe. Wrong constants in queue PI, queue base, CQ pointer, or CP fence registers can hang queue processing or corrupt command submission. Security-sensitive properties and the indirect APB gateway require careful mask coverage. The generated names, including misspellings such as `CHOISE`, should be treated as fixed generated interface.

## Test Signals

Signals include successful compile, NIC7 queue submissions writing the expected producer-index offsets, clean stop/stall transitions via `GLBL_CFG1`, `GAUDI_EVENT_NIC3_QM1` handled as `NIC3_QM1`, security masks including this instance's non-secure properties and doorbells, and stable hardware runs with no unexpected CP fence or arbitration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic3_qm1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic4_qm0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic4_qm0_regs.h

## Purpose

`nic4_qm0_regs.h` defines the auto-generated register constants for the Gaudi `NIC4_QM0` QMAN block. It provides the driver's symbolic view of the QM0 queue manager attached to NIC4. The local offsets run from `mmNIC4_QM0_GLBL_CFG0 0xDE0000` through `mmNIC4_QM0_GLBL_MEM_INIT_BUSY 0xDE0D00`; `gaudi_blocks.h` defines `mmNIC4_QM0_BASE 0x7FFCDE0000ull`, section `0x2000`, and max offset `0xD040`.

## Important APIs, Types, and Macros

This is a macro-only register map. It defines global configuration/protection/security/status registers; four producer queue register sets for base, size, producer/consumer indexes, configuration, ARUSER, and status; five completion queue register sets for configuration, status, pointer, transfer size, control, latched state, and IFIFO count; five command-processor register sets for message bases, LDMA offsets, fences, current instruction, barriers, debug, and AXI user properties; arbitration configuration, WRR weights, credits, choice offsets, master/slave controls, message attributes, status, and errors; and miscellaneous CGM, CSMR, HBW/LBW rate-limit, local range, AXCACHE, indirect-gateway, global error, and memory-init registers.

## Control Flow and Integration

The header is passive. `gaudi.c` writes `mmNIC4_QM0_GLBL_CFG1` as part of stop/stall handling for initialized `HW_CAP_NIC8`. Doorbell routing for `GAUDI_QUEUE_ID_NIC_8_0...GAUDI_QUEUE_ID_NIC_8_3` uses `mmNIC4_QM0_PQ_PI_0` plus a lane offset. Error routing maps `GAUDI_EVENT_NIC4_QM0` to `mmNIC4_QM0_BASE` and sends the event to common QMAN diagnostics/recovery. Security code references the same offsets to build register access masks.

## State and Persistence Behavior

No software state is defined here. The hardware state represented by these offsets includes queue ring location/size/progress, completion ring pointers, command-processor state and fences, arbitration scheduler credits, status/error registers, and memory initialization. Configuration and property writes persist in the QMAN hardware until reset or later programming.

## Dependencies

`gaudi_regs.h` includes this header, and `gaudi_blocks.h` defines the full base address. Runtime users also rely on common QMAN bit masks, `HW_CAP_NIC8`, queue and async event definitions, and MMIO read/write helpers. The file itself has no include dependencies other than its guard.

## Risks

Because `NIC4_QM0` is near the end of the NIC QMAN address range, copy/paste mistakes can accidentally target `NIC3` or `NIC4_QM1`. Queue doorbells, CP controls, and security property registers are sensitive to exact offsets. Generated register names should not be normalized or renamed manually. Any protection-mask omission can accidentally expose QMAN control registers to non-secure access.

## Test Signals

Expected evidence includes build success, correct NIC8 queue doorbells from `mmNIC4_QM0_PQ_PI_0`, stop writes to `GLBL_CFG1`, correct `GAUDI_EVENT_NIC4_QM0` logging and recovery, protection masks for this window, and stress tests without QMAN global, CP, or arbitration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic4_qm0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic4_qm1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic4_qm1_regs.h

## Purpose

`nic4_qm1_regs.h` defines the generated MMIO offsets for the Gaudi `NIC4_QM1` QMAN block, the QM1 queue manager for the last NIC instance covered by this group. Its local range starts at `mmNIC4_QM1_GLBL_CFG0 0xDE2000` and ends at `mmNIC4_QM1_GLBL_MEM_INIT_BUSY 0xDE2D00`. `gaudi_blocks.h` maps the full base as `mmNIC4_QM1_BASE 0x7FFCDE2000ull`, with section size `0x2000` and max offset `0xD040`.

## Important APIs, Types, and Macros

The file exports only register-offset macros. The 406 definitions follow the shared QMAN structure: global config, protection, properties, statuses, and message enables; PQ base/size/PI/CI/config/ARUSER/status for four producer queues; CQ config/status/pointer/transfer/control and IFIFO counters for five completion queues; CP message-base, LDMA, fence, current-instruction, barrier, debug, ARUSER, and AWUSER registers for five command processors; arbitration WRR, credit, choice, routing, message, status, error, and credit-status registers; and CGM, strict priority, rate limiting, local range, AXCACHE, indirect APB, global error, and memory-init registers.

## Control Flow and Integration

There is no executable code in the header. In the driver, `mmNIC4_QM1_GLBL_CFG1` is used to stop/stall the QMAN when `HW_CAP_NIC9` is present. Queue submission for `GAUDI_QUEUE_ID_NIC_9_0...GAUDI_QUEUE_ID_NIC_9_3` writes doorbells starting at `mmNIC4_QM1_PQ_PI_0`. Async error handling maps `GAUDI_EVENT_NIC4_QM1` to `mmNIC4_QM1_BASE`, labels the block `NIC4_QM1`, and calls common QMAN error handling. Security setup uses this instance's global and non-secure property offsets when computing protection masks.

## State and Persistence Behavior

The file does not persist C state. It names live MMIO registers whose values persist in the device across queue operations until reset or reprogramming. Important mutable state includes queue indexes and base/size registers, completion queue pointers and controls, command-processor fences and current instruction addresses, arbitration credits and routing, global error capture, and memory-init busy state.

## Dependencies

The header is part of the aggregate Gaudi register set through `gaudi_regs.h`. It relies on `gaudi_blocks.h` for the full physical/MMIO block base. Consumers use shared QMAN masks, Gaudi queue IDs, `HW_CAP_NIC9`, async event `GAUDI_EVENT_NIC4_QM1`, and low-level MMIO helpers.

## Risks

This instance is the final NIC QMAN in the Gaudi NIC set, so off-by-one NIC capability, queue ID, or event mappings can leave it uninitialized or can direct traffic into the wrong block. Security/property and indirect-gateway registers are sensitive. Doorbell offsets must remain exactly aligned at four-byte intervals from `PQ_PI_0`. Manual edits to generated names or offsets would carry high hardware risk.

## Test Signals

Signals include compile coverage, NIC9 queue doorbells landing at `mmNIC4_QM1_PQ_PI_0 + lane * 4`, QMAN stop writes through `GLBL_CFG1`, `GAUDI_EVENT_NIC4_QM1` reported and recovered as this block, security masks for `GLBL_NON_SECURE_PROPS_*` and `PQ_PI_0`, and stress or hardware validation runs without CP, arbitration, or global QMAN error causes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic4_qm1_regs.h -->
