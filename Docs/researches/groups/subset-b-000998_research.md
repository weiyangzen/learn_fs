# subset-b-000998 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_reset_conf_masks.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_reset_conf_masks.h

### Purpose
`psoc_reset_conf_masks.h` is an auto-generated Gaudi2 PSOC reset-controller bitfield catalog. It gives the driver named `SHIFT` and `MASK` constants for reset-source enable registers, unit reset registers, and per-instance clock/reset control registers.

### Important APIs, Types, And Functions
The file exports only preprocessor macros. The first large group maps reset-source enable fields for units such as PSOC, CPU, ARC, SIF, SRAM, PCIe, TPC, HBM, DMA, rotator, sync manager, video decoder, NIC, and NIC sub-blocks. Each reset source uses an `EN_SHIFT` of 0 and an `EN_MASK` sized to the unit fan-out, for example one bit for singleton units, `0x3` for two-instance blocks, `0xF` for four-instance blocks, `0x3FF` for ten video decoders, and `0xFFF` for NIC macros. Later groups expose `SW_ALL_RST`, `UNIT_RST_N`, and `<UNIT>_UNIT_RST` fields, followed by `<UNIT>_<index>_CLK_RST_CTRL_RST_SEL_MASK` and `CLK_DIS_MASK` fields.

### Control Flow
There is no executable control flow. Runtime reset flow is controlled by callers writing registers from `psoc_reset_conf_regs.h` with these masks: enable which hardware reset causes apply to each unit, assert/deassert software or unit resets, choose a reset source with `RST_SEL`, and gate clocks with `CLK_DIS`.

### State, Persistence, And Dependencies
This header stores no state. Its constants mutate persistent device state only when used by register writes. It is coupled to the generated reset address map and to the Gaudi2 hardware reset topology; the fan-out width in each mask must match the number of instances exposed elsewhere in `gaudi2.h`.

### Integration Points
The macros integrate with low-level reset, error recovery, FLR, watchdog, firmware reset, ECC double-error reset, and clock-gating paths. They also support bring-up and debug code that needs to isolate a single engine instance instead of resetting a whole unit group.

### Risks
Because the file is generated and repetitive, the main risks are stale generated masks, mismatches between instance counts and mask widths, using a group mask as a singleton bit, and confusing active-low `UNIT_RST_N` semantics with active-high reset controls. Writes to reset and clock-gating fields can stop engines, PCIe-facing blocks, memory controllers, or firmware-visible ARC blocks until a reset sequence repairs them.

### Test Signals
Useful signals are successful driver probe after reset configuration, FLR recovery, watchdog reset handling, ECC double-error reset routing, per-engine reset of TPC/DMA/rotator/NIC blocks, clock-gate toggling without hangs, and register readback showing only intended bits changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_reset_conf_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_reset_conf_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_reset_conf_regs.h

### Purpose
`psoc_reset_conf_regs.h` is the generated address map for the Gaudi2 PSOC reset configuration block. It names the memory-mapped registers that control reset-source policy, software/unit reset assertion, and per-instance clock/reset controls.

### Important APIs, Types, And Functions
The file exports `mmPSOC_RESET_CONF_*` address macros only. It begins with repeated eight-register policy blocks per unit: `PRSTN`, `SOFT`, `FW`, `WD`, `MNL`, `FLR`, `ECC_DERR`, and `SW` reset configuration. It then defines global reset controls such as `SOFT_RST`, `SW_ALL_RST`, and `UNIT_RST_N`, per-unit reset registers such as `ROTATOR_UNIT_RST`, and per-instance `*_CLK_RST_CTRL` registers for PSOC, CPU, ARC, SIF, SRAM, PCIe, TPC dividers, HBM dividers/controllers, PLLs, MME, MSS, TPCs, HIF/HMMU, XBARs, SFT/XFT/TFT, DMA engines, ARC subsystems, rotators, sync managers, video decoders, NIC macros, NIC ports, and NIC channels.

### Control Flow
There is no code path inside the header. Driver reset flow uses these addresses to configure which reset sources propagate, to trigger software or all-unit resets, and to poll or program unit-specific reset state. The paired mask header defines the bit meanings for the same registers.

### State, Persistence, And Dependencies
The header has no in-memory state. Writes to these addresses change hardware reset and clock state and therefore persist until later register writes or hardware reset. It depends on generated Gaudi2 register naming conventions and on callers applying the matching bit masks.

### Integration Points
This block is central to device initialization, teardown, firmware reset handshakes, PCIe FLR behavior, watchdog/ECC recovery, and per-engine quiesce/reset procedures. It intersects with `gaudi2.h` instance counts and with event/error paths that decide whether reset is needed.

### Risks
Address mistakes have high blast radius because many adjacent registers control destructive resets. The repeated layout encourages computed offsets, but callers must respect holes and unit-specific instance counts. A write intended for a clock gate can accidentally select a reset source or assert reset if the wrong address family is used.

### Test Signals
Probe and warm-reset tests should verify all critical units return to usable state, FLR leaves PCIe accessible, watchdog and firmware reset paths recover, engine-specific resets do not affect neighboring instances, and readback after writes matches mask expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_reset_conf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_timestamp_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_timestamp_regs.h

### Purpose
`psoc_timestamp_regs.h` defines the generated register addresses for the Gaudi2 PSOC timestamp counter block, a memory-mapped timer used for device time reads and counter control.

### Important APIs, Types, And Functions
The file exports `mmPSOC_TIMESTAMP_CNTCR`, `CNTSR`, `CNTCVL`, `CNTCVU`, `CNTFID0`, and CoreSight-style peripheral/component ID registers `PIDR*` and `CIDR*`. There are no C functions or types.

### Control Flow
The header has no executable flow. Callers typically disable/enable the counter through `CNTCR`, read the 64-bit counter from `CNTCVU` and `CNTCVL`, inspect status with `CNTSR`, and use `CNTFID0` as the frequency register.

### State, Persistence, And Dependencies
State lives in the hardware counter and control registers, not in this header. The counter value persists and increments according to the timestamp clock while enabled. Correct 64-bit reads depend on caller ordering or retry logic around upper/lower register reads if rollover is possible.

### Integration Points
Cross-references in older HabanaLabs device code show device time assembled from `CNTCVU` and `CNTCVL`; Gaudi2 code can use the same generated register naming. The timestamp block supports profiling, synchronization, diagnostics, and firmware/host correlation.

### Risks
The main risks are non-atomic 64-bit counter reads, using the wrong base or offset when programming control registers, and assuming a frequency without reading or configuring `CNTFID0`. Reset or clock gating of the timestamp block can break time continuity.

### Test Signals
Tests should confirm monotonic device-time reads, stable upper/lower rollover behavior, expected frequency, counter disable/enable effects, and sane PID/CID values during hardware bring-up diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_timestamp_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_desc_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_desc_regs.h

### Purpose
`rot0_desc_regs.h` defines the descriptor-register address map for Gaudi2 rotator instance 0. These registers describe an image rotation/warp job, completion message behavior, AXI attributes, and descriptor push.

### Important APIs, Types, And Functions
The exported macros cover context ID, input/output image base addresses, transform configuration, sine/cosine and affine matrix coefficients, input/output image geometry, strides, stripes, centers, background/padding, completion message address/data/AWUSER, idle state, read/write AXUSER fields, output window and buffer control, mesh image configuration, precision and clamping controls, and `PUSH_DESC`.

### Control Flow
There is no C control flow. Hardware flow is descriptor-driven: the driver writes a complete descriptor register set, configures completion messaging, then writes `PUSH_DESC` to submit work to the rotator. Status/idle registers indicate whether the descriptor path is ready or finished.

### State, Persistence, And Dependencies
Descriptor state is held by hardware registers until overwritten, consumed, or reset. Address fields are split low/high, so callers must program coherent 64-bit device addresses and AXUSER attributes. The header depends on matching rotator global registers and masks for status, error, and halt handling.

### Integration Points
The descriptor block integrates with queue-manager command submission, completion queues, memory-management/AXUSER programming, and rotator error handling. Security code also treats the rotator register ranges as protected MMIO windows.

### Risks
Partial descriptor programming can submit malformed jobs. Geometry, stride, mesh, and coefficient registers are tightly coupled; inconsistent values can cause out-of-bounds reads/writes or wrong image output. Completion message address/AWUSER mistakes can corrupt host-visible queues or fail to notify the driver.

### Test Signals
Useful tests include known-angle rotation outputs, mesh-mode transforms, completion interrupt/message delivery, idle-state polling, invalid descriptor rejection, address high/low programming, and reset recovery after a halted rotator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_desc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_masks.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_masks.h

### Purpose
`rot0_masks.h` defines bit positions and masks for Gaudi2 rotator instance 0 global control/status registers. It is the field companion to `rot0_regs.h`.

### Important APIs, Types, And Functions
The macros cover KMD-mode enable, completion queue enable/address/data/AWUSER/AXI attributes, completion message threshold and AXI attributes, writeback AXI attributes, stop-on-error, error status bits for rotator and QMAN HBW/LBW faults, WBC/RSB/MRSB maximum outstanding and rate-limit fields, empty/AXI-idle status, monitoring counters/timestamps/context IDs, MSS halt/status, SEI/SPI status and masks, pad-calculation disable, QMAN force-stop, clock-enable disable bits, and MSS halted status.

### Control Flow
There is no executable flow. Callers use these fields while enabling the rotator, configuring completion behavior, tuning read/write buffering, masking or reading interrupts, stopping on errors, forcing QMAN stop, and polling empty/idle/halt state.

### State, Persistence, And Dependencies
The header stores no state. Writes using these masks alter persistent rotator hardware state until reprogrammed or reset. It depends on `rot0_regs.h` addresses and on callers using read/modify/write for fields that share a register.

### Integration Points
These fields connect descriptor submission, rotator completion queues, MSS halt handling, SEI/SPI interrupt processing, error recovery, clock gating, and performance monitoring. Driver-level composed masks may wrap these generated fields for common idle or halt checks.

### Risks
Some fields are status-only while others are write controls; using a status mask as a write value can be harmful. Shared AXI fields require preserving unrelated cache/protection bits. Interrupt mask polarity must be confirmed before enabling or suppressing SEI/SPI signals. Force-stop and halt bits can leave in-flight descriptors incomplete.

### Test Signals
Signals include successful KMD-mode enable, completion queue operation, correct interrupt mask/status behavior, stop-on-error triggering, idle/empty polling matching actual work completion, rate limiter configuration readback, and clean recovery from forced halt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_arc_aux_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_arc_aux_regs.h

### Purpose
`rot0_qm_arc_aux_regs.h` defines the auxiliary register map for the ARC processor attached to rotator 0's queue manager. It covers ARC control, address windows, interrupts, ECC diagnostics, queues, bus overrides, and fork/region configuration.

### Important APIs, Types, And Functions
The exported address macros include run/halt request and acknowledgement, reset vector, debug mode, cluster/ARC number, wake events, DCCM system base, CTI controls, ARC reset request, SRAM/PCIe/CFG/HBM address windows and offsets, general-purpose windows, cache overrides, context IDs and offsets, software interrupts, IRQ masks, SEI/REI status/clear/mask/halt fields, ECC error addresses/syndromes, LBW termination diagnostics, scratchpads, CBU/LBU counters and AXI override fields, DCCM queues 0-7 with base/size/PI/CI/push/occupancy/valid-entry registers, queue warning/alert/drop controls, APB protection, LBW and CBU fork windows, ARC region config, DCCM secure region controls, AXI ordering controls, and ARC engine BUSER/DCCM controls.

### Control Flow
The header itself has no logic. Runtime flow uses these registers to bring the ARC out of reset, map memory windows, deliver software interrupts, exchange queue entries through DCCM queues, service or mask ARC/QMAN interrupts, and diagnose bus/ECC faults.

### State, Persistence, And Dependencies
State lives in ARC auxiliary hardware and DCCM queue registers. Queue producer/consumer indices, scratchpads, interrupt masks, and address-window configuration persist until firmware, driver, or reset changes them. This header depends on QMAN register maps, ARC firmware expectations, and security policy for protected MMIO ranges.

### Integration Points
Cross-references show security code whitelisting ranges from this header. It integrates with firmware boot, ARC command queues, error collection, protected access checks, and queue-manager completion/interrupt paths.

### Risks
Misprogrammed address windows or AXI overrides can expose wrong memory or break ARC firmware access. Queue PI/CI bugs can deadlock command exchange. Interrupt mask or clear mistakes can hide fatal ARC errors. DCCM secure-region and APB protection fields have security impact.

### Test Signals
Bring-up tests should verify ARC halt/run handshakes, reset-vector execution, software interrupt delivery, DCCM queue traffic, ECC fault reporting, bus termination diagnostics, protected-region enforcement, and recovery after ARC/QMAN errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_arc_aux_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_axuser_nonsecured_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_axuser_nonsecured_regs.h

### Purpose
`rot0_qm_axuser_nonsecured_regs.h` names the non-secured AXUSER attribute registers for rotator 0's queue manager. These registers describe how QMAN HBW/LBW transactions are tagged on the fabric.

### Important APIs, Types, And Functions
The macros cover HB ASID, MMU bypass, strong ordering, no-snoop, write reduction, read atomic, QoS, reserved fields, EMEM compact page, core ID, end-to-end coordination, write/read override low/high words, and LB coordination/lock/reserved/override registers.

### Control Flow
There is no code flow. QMAN initialization or security setup writes these addresses so subsequent queue-manager transactions carry the intended AXUSER attributes. Override registers can replace default fabric attributes for read/write paths.

### State, Persistence, And Dependencies
The state is hardware transaction-attribute configuration. It persists until reset or reprogramming and directly affects memory translation, ordering, snooping, QoS, and security classification. It depends on Gaudi2 MMU/ASID conventions and AXUSER bit definitions shared across other generated headers.

### Integration Points
The header integrates with queue-manager setup, protected/non-secured access policy, MMU bypass handling, fabric QoS, and debug/security code that verifies allowed register ranges.

### Risks
Incorrect ASID or MMU-bypass attributes can route accesses through the wrong address space or bypass translation unexpectedly. Strong-order/no-snoop/QoS misconfiguration can cause performance regressions or coherency surprises. Override fields are especially risky because they can affect every QMAN transaction.

### Test Signals
Signals include successful queue DMA through expected ASID, correct MMU fault behavior when bypass is disabled, no unauthorized non-secured access, expected ordering for completion writes, and register readback after context switches or reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_axuser_nonsecured_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_cgm_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_cgm_regs.h

### Purpose
`rot0_qm_cgm_regs.h` defines the small clock-gating-manager register block for rotator 0's queue manager.

### Important APIs, Types, And Functions
It exports three address macros: `mmROT0_QM_CGM_CFG`, `mmROT0_QM_CGM_STS`, and `mmROT0_QM_CGM_CFG1`. There are no C functions or types.

### Control Flow
The header contains no logic. Driver code writes configuration registers to enable or tune QMAN clock gating and reads status to confirm the block is gated, ungated, or idle as expected.

### State, Persistence, And Dependencies
Clock-gating policy and status live in hardware. Configuration persists until reset or subsequent writes. The block depends on the rotator QMAN being idle-safe before aggressive gating is enabled.

### Integration Points
This register block integrates with power management, reset paths, idle checks, and queue-manager bring-up/teardown. It complements the wider QMAN and rotator status registers.

### Risks
Enabling clock gating while queues or ARC communication are active can cause timeouts or lost progress. Misreading status may make reset code assume the block is idle when transactions are still in flight.

### Test Signals
Useful tests verify queue submission before and after clock-gating transitions, idle status consistency, power-management entry/exit, and recovery from reset with default CGM settings restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_cgm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_regs.h

### Purpose
`rot0_qm_regs.h` is the generated register address map for rotator 0's queue manager. It exposes the MMIO surface used to configure queues, command processors, completion queues, arbitration, ARC completion paths, error reporting, rate limiting, indirect APB access, and performance counters.

### Important APIs, Types, And Functions
The macros include global configuration/status/error registers, error message enables and protection, four PQ base/size/PI/CI/config/status banks, five CQ config/status/pointer/transfer-size/control banks, CP message bases, fence read-data/count banks, CP barrier/LDMA/CQ offsets, CP status/current-instruction/predicate/debug/credit/input-data registers, PQC HBW/LBW bases and push data, arbiter masks/config/choice/weights/credit/choice-offset/error/status registers, strict-priority CSMR config, ARC CQ config/pointers/status/message bases, address override and shadow CI registers, CP configuration/watchdog/switch controls, ARC/local/engine/QMAN base addresses, PQC status, SEI status/mask, global error address/write-data, L2H compare/mask, local-range, HBW/LBW rate limiters, indirect gateway registers, and free/idle performance counters.

### Control Flow
The header has no executable flow. Runtime QMAN flow programs PQs and CQs, configures CP and fence behavior, sets arbitration and credits, enables error reporting/protection, updates producer indices to submit work, watches consumer/status registers, and services errors or SEI events.

### State, Persistence, And Dependencies
All state is in the hardware queue manager. Queue bases, sizes, PI/CI values, CP state, arbiter credits, masks, and performance counters persist until driver writes or reset. The header depends on matching QMAN masks, ARC auxiliary registers, AXUSER attributes, CGM controls, and common HabanaLabs queue abstractions.

### Integration Points
Security code references many of these addresses when defining protected rotator register ranges. The queue map integrates with command submission, completion handling, firmware/ARC communication, device reset, error handling, performance collection, and async event mapping such as `GAUDI2_EVENT_ROTATOR0_ROT0_QM`.

### Risks
Queue programming bugs can corrupt command streams or completion queues. PI/CI races can hang work submission. Arbiter and credit misconfiguration can starve masters. Error-message masks and protection bits can either hide real faults or generate noisy interrupts. Indirect gateway misuse can touch unintended APB targets.

### Test Signals
High-value tests include descriptor submission through all PQs, CQ completion and CI updates, fence and barrier behavior, QMAN error injection, arbiter fairness, reset while queues are active, SEI interrupt delivery, protected-register access checks, and performance counter sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_regs.h

### Purpose
`rot0_regs.h` defines the global register addresses for Gaudi2 rotator instance 0. It controls rotator mode, completion messaging, AXI attributes, error reporting, buffering, MSS halt/interrupt state, QMAN force-stop, and clock controls.

### Important APIs, Types, And Functions
The macros name KMD mode, completion queue enable/address/data/AWUSER/AXI, completion message threshold/AXI, writeback AXI, error config/status, WBC/RSB/MRSB outstanding/rate-limit/inflight/occupancy/info/monitor registers, MSS halt/status/mask registers for SEI/SPI, pad calculation disable, QMAN config, clock enable, and MSS status.

### Control Flow
There is no C logic. Driver flow uses these addresses to enable the rotator, configure completion writes, tune buffering, detect and mask interrupts, force-stop QMAN when needed, poll idle/empty state, and halt/resume the MSS sub-blocks during recovery.

### State, Persistence, And Dependencies
State is persistent hardware configuration and status. It depends on `rot0_masks.h` for bit meanings and on descriptor/QMAN headers for the work-submission path. Reset clears or reinitializes these registers according to hardware defaults.

### Integration Points
This is the top-level rotator MMIO block used by initialization, error handling, completion processing, power/reset management, and security register-range definitions.

### Risks
Incorrect completion queue configuration can lose job completion notifications. Force-stop and halt controls can strand in-flight memory writes. Error-status interpretation depends on the matching masks and interrupt polarity. Clock controls can make later MMIO polling unreliable if used at the wrong time.

### Test Signals
Signals include KMD-mode enable readback, completion message delivery, WBC/RSB/MRSB idle status after jobs, SEI/SPI status/mask behavior, QMAN force-stop recovery, and clean reset of rotator 0 without affecting rotator 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/xbar_edge_0_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/xbar_edge_0_regs.h

### Purpose
`xbar_edge_0_regs.h` defines the generated register address map for Gaudi2 XBAR edge instance 0. It configures low-bandwidth/debug routing windows, HBM/PC bit placement, arbitration, rate limiting, credit state, and data-width conversion behavior.

### Important APIs, Types, And Functions
The macros cover LBW and DBG base/mask pairs for HIF, HMMU, EDMA, HBM, and XBAR targets; internal address routing registers; EMEM/HBM and EMEM/PC bit locations; HIF write response channel location; HBW master arbitration weight; MMU page-cache index maps; MMU read/write low-latency arbitration; HBM user response overrides; read and write rate limiters 0-11; end-to-end credit slave registers; credit debug; upscale/down-conversion controls; and down-conversion LFSR configuration.

### Control Flow
There is no executable code. Driver/security setup writes the address-window and conversion registers to route transactions across the XBAR, then may tune rate limiting, arbitration, and credits. Diagnostic code reads debug and credit registers.

### State, Persistence, And Dependencies
All state is XBAR hardware configuration. It persists until reset or reprogramming and affects fabric routing and memory access behavior. It depends on device address maps, HBM/PCIe layout, MMU configuration, and security policy.

### Integration Points
Cross-references show Gaudi2 security code enumerating XBAR edge ranges and selected conversion registers. The block integrates with memory fabric setup, protected register access, MMU/HIF/HBM routing, rate limiting, and debug flows.

### Risks
Bad base/mask programming can misroute MMIO or memory traffic. Rate limiter and arbitration mistakes can throttle or starve engines. Data-width conversion and LFSR settings can affect protocol correctness. Security exposure is high because XBAR routing defines which masters can reach which targets.

### Test Signals
Tests should cover expected access through each LBW/DBG window, HBM and PCIe traffic routing, MMU page-cache mapping, rate limiter behavior under load, security register-range enforcement, and no regressions in bandwidth or fabric error counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/xbar_edge_0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/xbar_mid_0_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/xbar_mid_0_regs.h

### Purpose
`xbar_mid_0_regs.h` defines the generated register address map for Gaudi2 XBAR mid instance 0. It has the same functional register families as the edge XBAR block but at the mid-instance base address.

### Important APIs, Types, And Functions
The exported macros include LBW/DBG base and mask windows for HIF, HMMU, EDMA, HBM, and XBAR peers; internal routing registers; EMEM bit-location controls; HIF response channel placement; HBW arbitration weight; MMU page-cache index mapping and low-latency arbiter controls; HBM response overrides; read/write rate limiter banks; end-to-end credit registers; and upscale/down-conversion LFSR controls.

### Control Flow
The header contains no logic. Initialization and security paths program routing windows and conversion settings, while performance/debug paths inspect or adjust arbitration, rate limiting, and credit state.

### State, Persistence, And Dependencies
State is persistent XBAR hardware configuration. The register map depends on the broader fabric topology and on correct alignment with edge XBAR instances and duplicated XBAR blocks counted in `gaudi2.h`.

### Integration Points
Gaudi2 security code references `mmXBAR_MID_0_*` ranges. The map integrates with MMU/HIF/HBM routing, fabric protection, bandwidth management, and low-level debug.

### Risks
The mid and edge maps are structurally similar, so instance mixups are a realistic risk. Wrong base/mask or conversion settings can break routing across a central fabric segment and affect multiple engines. Rate-limit changes can create global performance artifacts.

### Test Signals
Test signals include register readback for mid instance 0, successful memory traffic through expected routes, security allow/deny behavior, bandwidth under load, no XBAR ECC/fatal async events, and comparison with edge-instance programming where symmetry is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/xbar_mid_0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2.h

### Purpose
`gaudi2.h` provides shared Gaudi2 constants for BAR IDs/sizes, physical and virtual address ranges, memory sizes, interrupt counts, queue-entry sizing, ASID limits, ARC counts, engine topology, and cache-line size.

### Important APIs, Types, And Functions
The header exports macros for SRAM/MSIX/DRAM BAR IDs and sizes, CFG base/size/region size, STM/SPI flash, scratchpad SRAM, PCIe firmware SRAM, BAR0 reserved window, SRAM and DRAM physical bases, DRAM VA hint mask, host physical windows, reserved virtual ranges for ARC on HBM/host and virtual MSI-X doorbells, the unexpected user-error MSI-X index, `GAUDI2_MSIX_ENTRIES`, QMAN PQ entry size, `MAX_ASID`, ARC CPU and DCCM details, DCORE and per-engine instance counts, TPC tensor counts, MME seed count, NIC macro/engine/port counts, and `DEVICE_CACHE_LINE_SIZE`.

### Control Flow
There is no executable flow. These constants parameterize driver initialization, memory mapping, queue sizing, interrupt allocation, topology iteration, virtual address reservation, and engine enumeration.

### State, Persistence, And Dependencies
The header stores no state. It is a central compile-time contract that must match silicon, firmware, generated register maps, and user-visible driver capabilities. Derived constants such as NIC engine/port counts build on base topology macros.

### Integration Points
The file is included by Gaudi2 driver code and aligns with generated register headers, async event IDs, queue-manager setup, MMU/VA management, MSI-X setup, ARC firmware loading, and engine discovery.

### Risks
Incorrect constants can cause invalid BAR mappings, memory-window overlap, queue mis-sizing, missing interrupts, wrong engine loops, or security holes in reserved VA regions. `MAX_ASID` and address masks are especially sensitive for isolation and MMU behavior.

### Test Signals
Signals include successful PCI BAR discovery, MMIO and DRAM mapping, correct MSI-X count, all expected engines enumerated exactly once, valid reserved VA allocation, queue entry alignment, ARC DCCM access, and NIC/TPC/MME counts matching firmware reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_async_events.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_async_events.h

### Purpose
`gaudi2_async_events.h` is an auto-generated enumeration of Gaudi2 asynchronous event IDs. It gives driver and firmware code stable numeric IDs for ECC, PCIe, AXI, PLL, MMU, HBM, TPC, MME, DMA, NIC, rotator, CPU, ARC, GPIO, and queue-manager events.

### Important APIs, Types, And Functions
The file defines `enum gaudi2_async_event_id` and terminates with `GAUDI2_EVENT_SIZE`. Event ranges include PCIe core/interface/PHY errors, TPC ECC and kernel/BMON/QM events, MME SBTE/control/WAP ECC and AXI/QM events, HDMA/KDMA/PDMA ECC/BMON/QM/core events, PSOC and SRAM events, HBM MC ECC/CATTRIP/SEI/SPI events, HMMU/PMMU ECC/page-fault/security/AXI events, decoder ECC/SPI/BMON/AXI events, HIF/NIC/SM/XBAR ECC/fatal/AXI events, PLL lock failures, PCIe reset/power-management/fatal events, rotator SERR/DERR/AXI/BMON/QM events, CPU firmware/status events, NIC engine status, ARC power/heartbeat, and `GAUDI2_EVENT_SIZE` for array sizing.

### Control Flow
There is no function logic. Runtime event handling uses these IDs as array indexes, switch keys, log identifiers, and firmware event numbers. Cross-references show `gaudi2P.h` allocating arrays sized by `GAUDI2_EVENT_SIZE` and `gaudi2.c` mapping queue IDs to QMAN async event IDs.

### State, Persistence, And Dependencies
The enum has no state, but its numeric values are an ABI-like contract with firmware, interrupt/event queues, and diagnostic tables. Event statistics arrays persist counts indexed by these values. The file depends on generated hardware event assignments remaining stable.

### Integration Points
It integrates with async event queue handling, interrupt reporting, health monitoring, reset/escalation policy, queue-manager error attribution, user-visible event logs, and firmware-to-host notifications.

### Risks
Renumbering or deleting enum values breaks firmware/driver interpretation and corrupts event-stat indexing. Sparse ranges and explicit gaps mean code must use `GAUDI2_EVENT_SIZE`, not assume dense subsystem-local ranges. Typos in generated names, such as `RSPONSE`, can become part of the source contract.

### Test Signals
Tests and diagnostics should verify event queue decoding, correct QMAN event mapping per queue, bounds checks against `GAUDI2_EVENT_SIZE`, event-stat increments for injected events, severity-specific recovery for SERR/DERR/fatal cases, and user logs naming the expected subsystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_async_events.h -->
