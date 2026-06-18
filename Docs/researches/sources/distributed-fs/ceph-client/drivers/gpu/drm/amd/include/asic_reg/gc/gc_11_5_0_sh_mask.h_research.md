# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002549`: lines 1-2578, `Docs/researches/chunks/subset-b-002549_research.md`
- `subset-b-002550`: lines 2579-5025, `Docs/researches/chunks/subset-b-002550_research.md`
- `subset-b-002551`: lines 5026-7369, `Docs/researches/chunks/subset-b-002551_research.md`
- `subset-b-002552`: lines 7370-9764, `Docs/researches/chunks/subset-b-002552_research.md`
- `subset-b-002553`: lines 9765-12372, `Docs/researches/chunks/subset-b-002553_research.md`
- `subset-b-002554`: lines 12373-14858, `Docs/researches/chunks/subset-b-002554_research.md`
- `subset-b-002555`: lines 14859-17371, `Docs/researches/chunks/subset-b-002555_research.md`
- `subset-b-002556`: lines 17372-19737, `Docs/researches/chunks/subset-b-002556_research.md`
- `subset-b-002557`: lines 19738-22220, `Docs/researches/chunks/subset-b-002557_research.md`
- `subset-b-002558`: lines 22221-24948, `Docs/researches/chunks/subset-b-002558_research.md`
- `subset-b-002559`: lines 24949-27593, `Docs/researches/chunks/subset-b-002559_research.md`
- `subset-b-002560`: lines 27594-30086, `Docs/researches/chunks/subset-b-002560_research.md`
- `subset-b-002561`: lines 30087-32527, `Docs/researches/chunks/subset-b-002561_research.md`
- `subset-b-002562`: lines 32528-35050, `Docs/researches/chunks/subset-b-002562_research.md`
- `subset-b-002563`: lines 35051-36579, `Docs/researches/chunks/subset-b-002563_research.md`

## Chunk Research

### subset-b-002549: lines 1-2578

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 1-2578

## Purpose

This chunk is generated AMD GC 11.5.0 register bitfield metadata. It contains no executable C code; it exports `#define` constants for hardware register field shifts and masks. Driver code combines these constants with the matching register-offset header and AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to compose and decode 32-bit MMIO register values.

The range covers the beginning of `gc_11_5_0_sh_mask.h`. It opens the include guard, defines the entire `gc_sdma0_sdma0dec` address block, and then starts the `gc_sdma0_sdma0hypdec` block. Functionally, this is the SDMA0 register layout for GC 11.5.0: global SDMA control/status, microcode version/checksum, power and clock-gating control, page/TLB/XNACK fault reporting, EDC/ECC diagnostics, queue reset/status, and the repeated queue register layout for SDMA0 queues 0 through 7. Although this repository path is under `ceph-client`, the file is AMD GPU driver hardware metadata, not filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, allocations, locks, or direct MMIO operations in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the in-register field mask.
- The macros describe fields only; callers need the companion offset definitions to know which MMIO address to access.

Major register groups in this chunk:

- Global SDMA0 control and identity: `SDMA0_DEC_START`, `SDMA0_F32_MISC_CNTL`, `SDMA0_UCODE_VERSION`, `SDMA0_GLOBAL_TIMESTAMP_LO/HI`, `SDMA0_POWER_CNTL`, `SDMA0_CNTL`, `SDMA0_CNTL1`, `SDMA0_ID`, and `SDMA0_VERSION`. These fields cover engine start, F32 wakeup, firmware version, timestamps, light-sleep/deep-sleep control, interrupt enables, byte-swap behavior, preemption, page-fault/null/retry timeout interrupts, and write-pointer polling frequency.
- Workaround, performance, and memory-layout controls: `SDMA0_CHICKEN_BITS`, `SDMA0_CHICKEN_BITS_2`, `SDMA0_GB_ADDR_CONFIG`, `SDMA0_GB_ADDR_CONFIG_READ`, `SDMA0_TILING_CONFIG`, `SDMA0_HASH`, `SDMA0_BA_THRESHOLD`, `SDMA0_CRD_CNTL`, and `SDMA0_RELAX_ORDERING_LUT`. These define burst sizing, 256-byte combine controls, copy overlap/RAW checking, fine-grained clock-gating overrides, address configuration, tiling/hash parameters, bus/address thresholds, credit limits, and relaxed ordering per packet class.
- Global ring/IB fetch helpers: `SDMA0_RB_RPTR_FETCH`, `SDMA0_RB_RPTR_FETCH_HI`, `SDMA0_IB_OFFSET_FETCH`, `SDMA0_PROGRAM`, and `SDMA0_SEM_WAIT_FAIL_TIMER_CNTL`. These expose ring read-pointer fetch offsets, indirect-buffer fetch offsets, a full-width program stream field, and the semaphore wait-fail timer.
- Status and diagnostics: `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, `SDMA0_STATUS3_REG`, `SDMA0_STATUS4_REG`, `SDMA0_STATUS5_REG`, `SDMA0_STATUS6_REG`, `SDMA0_QUEUE_STATUS0`, `SDMA0_INT_STATUS`, `SDMA0_FED_STATUS`, `SDMA0_AQL_STATUS`, and `SDMA0_CLOCK_GATING_STATUS`. These fields expose idle/full/stall states, command opcodes, copy-engine status, active queue IDs, WPTR polling exceptions, XNACK events, ECC/FED conditions, AQL signal FIFO state, and clock-gating state.
- Freeze, scheduling, watchdog, and reset controls: `SDMA0_FREEZE`, `SDMA0_PROCESS_QUANTUM0/1`, `SDMA0_GLOBAL_QUANTUM`, `SDMA0_WATCHDOG_CNTL`, `SDMA0_QUEUE_RESET_REQ`, and queue-local preemption/reset fields. These define engine freeze/preempt bits, per-process and global scheduling quantums, hang/command timeout buckets, and per-queue reset requests.
- Error-detection and correction: `SDMA0_EDC_CONFIG`, `SDMA0_EDC_COUNTER`, `SDMA0_EDC_COUNTER_CLEAR`, `SDMA0_UCODE_CHECKSUM`, `SDMA0_UCODE1_CHECKSUM`, and `SDMA0_FED_STATUS`. These cover EDC disable/interrupt control, single/double error flags across ucode, RB/IB command buffers, UTCL1 FIFOs, data LUTs, memory-bank buffers, split buffers, MC write-address FIFOs, and fetch/data/copy metadata paths.
- UTCL1, VM, and page fault/XNACK registers: `SDMA0_UTCL1_CNTL`, `SDMA0_UTCL1_WATERMK`, `SDMA0_UTCL1_TIMEOUT`, `SDMA0_UTCL1_PAGE`, `SDMA0_UTCL1_RD_STATUS`, `SDMA0_UTCL1_WR_STATUS`, `SDMA0_UTCL1_INV0/1/2`, `SDMA0_UTCL1_RD_XNACK0/1`, `SDMA0_UTCL1_WR_XNACK0/1`, `SDMA0_TLBI_GCR_CNTL`, `SDMA0_PHYSICAL_ADDR_LO/HI`, `SDMA0_HOLE_ADDR_LO/HI`, and `SDMA0_EA_DBIT_ADDR_*`. These define translation retry delays, invalidation controls, FIFO watermarks, page attributes, read/write translation status, invalidation request payloads, XNACK fault address/VMID/vector/flags, TLB/GCR command sizing and credits, physical-address reporting, VM hole addresses, and DBIT address indexing.
- Miscellaneous public registers: `SDMA0_ATOMIC_CNTL`, `SDMA0_ATOMIC_PREOP_LO/HI`, `SDMA0_SCRATCH_RAM_DATA/ADDR`, `SDMA0_TIMESTAMP_CNTL`, `SDMA0_PUB_DUMMY_REG0..3`, `SDMA0_F32_COUNTER`, `SDMA0_RLC_CGCG_CTRL`, `SDMA0_CE_CTRL`, and `SDMA0_ERROR_LOG`. These support atomic return interrupt timing, pre-operation data, scratch access, timestamp capture, dummy/debug registers, F32 counters, RLC clock-gating interrupt/hysteresis, copy-engine FIFO/watermark controls, and error logging.
- Queue register templates for `SDMA0_QUEUE0` through `SDMA0_QUEUE7`: each queue has ring-buffer control/base/read-pointer/write-pointer registers, RPTR writeback addresses, indirect-buffer control/base/offset/size/read-pointer registers, skip count, context status, doorbell enable/captured/offset fields, CSA address, schedule control, IB subremain, IB and RB preemption, dummy register, WPTR poll address, AQL control, minor pointer update, mid-command data registers `MIDCMD_DATA0..10`, and `MIDCMD_CNTL`. Queue 0's `CONTEXT_STATUS` includes a `USE_IB` bit that is absent from queues 1 through 7 in this chunk.
- The beginning of the hypervisor/SR-IOV decode block: `SDMA0_UCODE_ADDR`, `SDMA0_UCODE_DATA`, `SDMA0_BROADCAST_UCODE_ADDR`, `SDMA0_BROADCAST_UCODE_DATA`, `SDMA0_VM_CTX_LO/HI`, `SDMA0_ACTIVE_FCN_ID`, `SDMA0_VIRT_RESET_REQ`, and `SDMA0_VM_CNTL`. These describe ucode address/data access, broadcast ucode programming, VM context address registers, active VF/PF identification, virtual reset request bits, and VM command control. The chunk ends at the `SDMA0_F32_CNTL` comment, before that register's fields.

## Control Flow

This header has no runtime control flow. It participates in register access flows through inclusion and macro substitution:

1. GC 11.5.0 driver code includes the matching offset and shift/mask headers.
2. The caller selects a register offset for SDMA0 or an SDMA queue instance.
3. The caller composes or decodes a 32-bit value with these `__SHIFT` and `_MASK` macros, usually through common AMDGPU field helpers or explicit shifts.
4. The caller performs ordered MMIO reads/writes through AMDGPU register accessors while higher-level SDMA, KFD, VM, reset, interrupt, or virtualization code owns sequencing.

The control-flow-sensitive behavior is therefore in the consumers, not the header. For example, queue bring-up code programs base addresses, sizes, VMIDs, doorbells, write-pointer polling, and RPTR writeback before setting `RB_ENABLE`; teardown/reset paths clear enable bits or assert queue reset/preempt bits; interrupt paths use enable/status fields to route page faults, preemption, context-empty, frozen, and ECC/EDC events.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It names bit layouts for hardware state exposed by GC 11.5.0 SDMA0 registers.

The represented hardware state includes:

- Engine-wide configuration such as power management, interrupt enables, byte swapping, preemption policy, page-fault interrupt behavior, light sleep, clock gating, relaxed ordering, address hashing/tiling, and copy-engine controls.
- Firmware and diagnostic state such as ucode version/checksum, F32 instruction pointers/counters, FED/ECC/EDC flags, scratch RAM contents, dummy/debug registers, global timestamps, and error/status logs.
- Translation and memory-state controls such as UTCL1 invalidation, XNACK fault address and VMID, page attributes, TLB/GCR credits, physical-address reporting, VM hole addresses, DBIT address selection, and HBM page configuration.
- Queue state for eight SDMA0 queues: ring buffer base/high addresses, RPTR/WPTR values, read-pointer writeback addresses, IB base/offset/read pointer/size, CSA addresses, doorbell state, schedule IDs and context quantum, AQL packet sizing, minor pointer updates, queue context status, and saved mid-command data.
- Virtualization state at the tail of the chunk, including active function ID, VF/PF reset requests, VM context base address, and ucode programming/broadcast access.

Persistence is hardware-defined. Some fields are configuration that lasts until reset, power-gating, suspend/resume, queue teardown, or explicit reprogramming. Others are live status, hardware-owned pointers, counters, sticky error bits, write-one/self-clearing requests, or transient active-queue state. The masks do not encode read-only versus writable semantics, reset defaults, write-one-to-clear behavior, ordering requirements, or power-domain restrictions.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which supplies the register offsets corresponding to these field masks. The definitions also depend on common AMDGPU register-helper conventions for field packing/unpacking and SOC15 addressing.

Observed and expected integration points include:

- GC 11.5.0 support files such as `amdgpu/gfxhub_v11_5_0.c`, which include this generated mask header for generation-specific register definitions.
- AMDGPU SDMA initialization and ring-management code, which programs queue ring-buffer base, size, VMID, RPTR writeback, write-pointer polling, doorbells, IB controls, AQL controls, and enable bits.
- AMDKFD queue/MQD management paths for SDMA queues. Closely related GC/SDMA generations use `SDMA0_QUEUE0_RB_CNTL__RB_SIZE__SHIFT`, `SDMA0_QUEUE0_RB_CNTL__RB_VMID__SHIFT`, `SDMA0_QUEUE0_RB_CNTL__RPTR_WRITEBACK_ENABLE__SHIFT`, and write-pointer polling fields to build SDMA queue descriptors.
- VM, GFXHUB, and memory-management paths that need SDMA page attributes, UTCL1 invalidation/status, XNACK fault reporting, VMID fields, physical-address reporting, and TLB/GCR controls.
- Interrupt and recovery paths that enable and decode page-fault/null/retry timeout, semaphore wait, context-empty, frozen, IB/RB preempt, CP/MES, ECC/EDC, and copy-engine status events.
- Reset, preemption, and suspend/resume flows that inspect idle/status bits, active queue IDs, queue reset requests, freeze/preempt bits, queue context status, mid-command save data, and WPTR polling exceptions.
- SR-IOV/virtualization flows at the chunk tail that use function-ID, virtual reset, VM context, and broadcast ucode registers to separate PF/VF behavior.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. These masks must be paired with the GC 11.5.0 offsets; using another generation's offsets can compile but write wrong bits.
- The chunk boundary is artificial. It contains a full SDMA0 public decode block, but the hypervisor decode block is only partially present and ends before `SDMA0_F32_CNTL` fields.
- The macros are untyped constants. A mask from one register or queue instance can be accidentally applied to another value without compiler diagnostics.
- Whole-register writes are risky because registers mix configuration bits, enable bits, request bits, live status, counters, sticky errors, reserved fields, and hardware-owned pointer state.
- Queue address fields have alignment-sensitive shifts and masks. RPTR writeback, WPTR poll, CSA, and IB base addresses mask off low address bits; callers must pass correctly aligned GPU or system addresses.
- Queue size fields are encoded values, not necessarily raw byte counts. Incorrect unit conversion can cause ring wrap errors, stale pointers, or SDMA hangs.
- Doorbell offsets are masked and shifted. Wrong offsets can signal the wrong queue or fail to wake SDMA work.
- VMID, privilege, TMZ/preemption, PF/VF, and page-attribute fields affect isolation and fault routing. Incorrect programming can route memory requests to the wrong address space or break secure/virtualized queue behavior.
- Status fields can race with firmware, the scheduler, interrupts, queue teardown, reset, or user-mode doorbells. Consumers must own the relevant queue/engine sequencing before relying on snapshots.
- EDC/ECC/FED/XNACK flags may be sticky or clear-on-write depending on the register semantics, which are not described by the generated mask names.
- Workaround and clock-gating fields can change engine timing, polling behavior, or power state. They should be modified only by generation-specific initialization or validated workaround paths.
- Full-width masks such as `0xFFFFFFFFL` describe data, pointer, timestamp, or stream payload fields, not a guarantee that all values are safe to write.

## Test Signals

Useful validation signals for code using this chunk include:

- Build coverage for GC 11.5.0 include users, catching missing or stale SDMA0 macro names.
- Register trace comparison against known-good GC 11.5.0 SDMA initialization tables for `SDMA0_CNTL`, power/clock-gating controls, relaxed ordering, address configuration, UTCL1 controls, and queue ring registers.
- SDMA queue bring-up tests for queues 0 through 7 that verify ring base/size programming, RPTR/WPTR movement, RPTR writeback, WPTR polling, doorbell wakeups, and IB execution.
- AMDKFD SDMA queue tests for VMID assignment, AQL enable/packet sizing, queue scheduling quantum, context status, preemption, and queue reset.
- Interrupt tests that exercise page fault/null/retry-timeout, semaphore wait, context-empty, frozen, IB/RB preempt, CP/MES, and ECC/EDC/FED paths and verify both enables and status decoding.
- VM fault and XNACK tests that validate UTCL1 read/write status, invalidation commands, fault address/VMID/vector fields, TLB/GCR credits, and page attribute programming.
- Reset and recovery tests that freeze/preempt queues, assert queue reset requests, verify idle/status bits, and reinitialize SDMA0 queues after GPU reset or suspend/resume.
- SR-IOV tests for active function ID, VF/PF reset request bits, VM context address programming, and broadcast ucode access.
- Power-management tests that toggle light sleep and clock-gating paths while confirming SDMA progress, no lost doorbells, and expected clock-gating status.

### subset-b-002550: lines 2579-5025

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 2579-5025

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains C preprocessor constants only: each register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit hardware register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this line range.

The selected lines start at the body of `SDMA0_F32_CNTL`, then cover SDMA0 performance counter control/result registers, SDMA0 clock/power override bits, GRBM global graphics status/reset/error/trap/scratch registers, CP command-processor debug/status/FIFO/register-queue counters, PA/VGT/GE front-end controls, SQ/SQC/LDS/shader debug and watchpoint controls, SPI shader-processor counters/trap-screen/debug controls, TD/TA texture block controls, GDS status/protection/EDC registers, and the beginning of `DB_DEBUG`. The range ends after only the first several `DB_DEBUG` masks; the remaining masks continue after line 5025 in the adjacent chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 11.5.0 graphics IP and is not Ceph filesystem logic.

## Purpose

`gc_11_5_0_sh_mask.h` supplies field layouts for GC 11.5.0 registers. Driver code pairs these macros with register addresses from the matching `gc_11_5_0_offset.h` header, then usually uses helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` so register programming and diagnostics do not embed magic bit positions.

This chunk focuses on control, observability, fault reporting, and low-level debug for major graphics blocks:

- SDMA0 firmware/F32 and performance counter state: `SDMA0_F32_CNTL` controls F32 halt, checksum clear, thread reset/enable, and thread priorities. `SDMA0_PERFCNT_*` and `SDMA0_PERFCOUNTER*` define event selection, modes, enable/clear controls, result selection, and low/high counter result fields.
- SDMA0 clock override: `GFX_ICG_SDMA0_CTRL` exposes soft overrides for F32, performance-counter, copy-engine, dynamic, and register clocks.
- GRBM register-bus manager state: `GRBM_STATUS*`, `GRBM_SOFT_RESET`, clock/idle controls, read/write error attribution, trap address/data/mask registers, IH credits, UTCL2 invalidation ranges, invalid-pipe logging, fence ranges, scratch registers, and asynchronous VF violation state.
- CP command processor state: CPC/CPF/CP debug, busy, stalled, status, GRBM free-count, header dump, scratch indexed access, ring-buffer read/write pointer, queue threshold/availability, ROQ/STQ/MEQ stats, command index/data, and queue doorbell status macros.
- PA/VGT/GE front-end state: DMA FIFO depths, draw-init FIFO depth, memory-controller latency/timestamp controls, wave-dispatch/primitive configuration, UTCL1 controls/status, unit-disable and rate controls, geometry engine safe/status controls, shader-array configuration, and PA clipping/setup/scissor FIFO status.
- SQ/SPI shader state: SQ/SQC/LDS configuration, wave priority, FIFO sizes, arbitration, trap/watchpoint status, GL1H/SQG status, shader-rate config, interrupt masking, watchpoint address/control windows, indirect index/data, commands, SPI wave lifetime counters/status, load-balancer counters, WGP masks, export/scoreboard buffer sizes, active-wave counters, trap-screen base/mask/GPR windows, and crawler configs.
- TP and GDS state: TD/TA texture controls, power/status/scratch registers, GDS global status/enhancement, protection and VM-protection fault attribution, and EDC counters for GDS memory/input queue/GRBM/OA paths.
- RB depth-buffer debug state: the first part of `DB_DEBUG`, covering compression/read/HiZ/HiS/fast-Z/stencil/noop-cull/z-plane/sync disable and force fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the mask for that field in the register value.
- Register-address symbols live in the companion `gc_11_5_0_offset.h` header, commonly with `reg...` or `mm...` names matching the register.
- AMDGPU consumers use these constants through register helpers, direct MMIO helpers, ring packet writers, debug dump code, reset paths, perf counter paths, VM/fault handlers, and KFD/compute queueing code.

The chunk contains 2,172 `#define` entries across 244 register names: 1,093 shift macros and 1,079 mask macros. The address-block inventory is:

- `gc_sdma0_sdma0perfsdec`: SDMA0 performance-counter selector/configuration registers.
- `gc_sdma0_sdma0perfddec`: SDMA0 performance-counter low/high result windows.
- `gc_sdma0_sdma0pwrdec`: SDMA0 internal clock-gating override control.
- `gc_grbmdec`: GRBM status, reset, clock, trap, error, scratch, fence, invalidation, and violation registers.
- `gc_cpdec`: CP/CPC/CPF busy/stall/status/debug, queue, ring, threshold, and command registers.
- `gc_padec`: VGT, WD, GE, IA, PA, and shader-array front-end controls/status.
- `gc_sqdec`: SQ/SQC/LDS/SP/SQG controls, debug, interrupts, watchpoints, and indexed command/data registers.
- `gc_shsdec`: SX/SPI controls, EDC, wave lifetime, load-balancer, active-wave, trap-screen, and crawler registers.
- `gc_tpdec`: TD/TA texture block controls/status/scratch.
- `gc_gdsdec`: GDS configuration, status, protection fault, VM fault, and EDC registers.
- `gc_rbdec`: the opening `DB_DEBUG` bitfield definitions.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU is:

1. Select the GC 11.5.0 register headers for an ASIC with `IP_VERSION(11, 5, 0)`.
2. Choose the matching address macro from `gc_11_5_0_offset.h`.
3. Read a current register value, construct a register write, or prepare a command packet/debug dump/perf access.
4. Use the `__SHIFT` and `__MASK` pairs, normally through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract a single field.
5. Feed the resulting value into VM setup, GFX/SDMA bring-up, idle waits, reset, performance monitoring, KFD queue handling, trap/fault reporting, hang diagnostics, or power/debug configuration.

For SDMA and performance counters, consumers select events/modes, clear and enable counters, then read low/high result registers. For GRBM and CP status, consumers poll or snapshot busy/stalled/clean bits during idle waits, reset decisions, hang dumps, and debugfs-style diagnostics. For SQ/SPI/GDS/DB fields, consumers generally program debug controls, watchpoints, trap screens, counters, or decode fault/EDC status. Required ordering, delays, clear-on-read behavior, latching, and side-effect sequencing are not expressed in this header; those rules live in engine code and the hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware-owned state that is live, latched, sticky, or side-effectful depending on the register.

SDMA0 F32 and clock override fields affect active engine behavior while programmed. Halting or resetting F32 threads, clearing checksums, changing priorities, or overriding internal clocks can alter queue execution, firmware servicing, power behavior, or diagnostics until the fields are restored or the engine is reset.

Performance counter configuration fields persist selected events, modes, enable/clear state, and result-selection state while counters accumulate. Counter result registers expose hardware values that may require documented read ordering or latching to avoid torn high/low snapshots. This chunk can identify bit widths but cannot guarantee atomicity or saturation behavior.

GRBM and CP status fields are mostly volatile snapshots of busy, stalled, request-pending, free-count, FIFO, pointer, and active/clean state. Error, trap, invalid-pipe, write/read fault, violation, protection, and interrupt-status fields may be sticky until cleared through a documented sequence. `GRBM_SOFT_RESET`, `GRBM_PWR_CNTL2`, clock-gating controls, and CP queue controls have direct side effects and should not be handled as passive status.

Scratch, fence-range, trap-screen, watchpoint, indexed data, and GDS configuration registers can persist driver or firmware state across ordinary operation until overwritten, context-switched, power-gated, or reset. In virtualized/SR-IOV contexts, VF/VFID/VMID/SSRCID/TMZ/security-write fields must be decoded exactly because they attribute faults, resets, and illegal accesses to specific functions or address spaces.

Reserved and `UNUSED` fields appear throughout the generated map. Callers should preserve such bits during read-modify-write unless the hardware documentation requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` provides the matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c` directly includes both `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h` for GC 11.5.0 VM/GART/fault setup and demonstrates the intended `REG_SET_FIELD`/`REG_GET_FIELD` usage.
- `gfx_v11_0.c`, `gmc_v11_0.c`, `mes_v11_0.c`, `amdgpu_discovery.c`, KFD device selection, PSP/ucode loading, PM/SMU code, and display family selection all contain `IP_VERSION(11, 5, 0)` integration points that select GC 11.5.0 behavior, firmware, or family-specific paths.
- Common AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD` perform the actual MMIO access and field packing/extraction.

Runtime integration points include SDMA0 performance monitoring and firmware debug, graphics idle waits, GPU reset/hang recovery, GRBM read/write error logging, CP queue and command processor diagnostics, CP interrupt and ring-pointer handling, KFD queue/debug operations, shader watchpoint/trap support, GDS aperture/fault handling, GDS EDC reporting, texture/front-end status dumps, VM protection fault reporting, and depth-buffer debug/golden-register programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can write the wrong bit, corrupt hardware state, or decode misleading diagnostics.
- This chunk has partial-boundary coverage. It starts immediately after the `//SDMA0_F32_CNTL` comment and ends before all `DB_DEBUG` masks are present, so file-level research must merge this with adjacent chunks.
- Side-effect registers are intermixed with passive status registers. Misusing `SDMA0_F32_CNTL`, `GFX_ICG_SDMA0_CTRL`, `GRBM_SOFT_RESET`, `GRBM_PWR_CNTL2`, CP queue controls, SQ commands, SPI trap/crawler controls, or `DB_DEBUG` can hang active work, change timing, lose debug state, or perturb rendering.
- Busy/stalled/free-count/status bits are volatile. Polling code must handle transitions, clock-gated blocks, in-flight command streams, and blocks that legitimately remain busy during firmware activity.
- High/low result and pointer registers can be race-prone if read without the documented latch/order sequence. This applies to performance counters, instruction pointers, ring read pointers, and trap/status snapshots.
- Address and identity fields are often encoded, aligned, or split. Treating shifted fields as raw byte addresses can produce plausible but wrong trap, fence, context, or fault addresses.
- Virtualization/security attribution fields are high impact. VF/VFID/VMID/SSRCID/TMZ/security-write bits in GRBM, GDS, and CP paths must remain exact for SR-IOV isolation and fault reporting.
- Reserved and `UNUSED` masks cover large portions of several registers. Full-register writes that do not preserve undocumented bits may introduce ASIC-specific regressions.
- Symmetric-looking status families across CP pipes, ME/MEC engines, SPI wave counters, and GDS OA paths are prone to copy/generator mistakes; one wrong field width can make only one pipe or WGP class misreport.
- `DB_DEBUG` fields can disable compression, fast-Z/stencil, z-plane optimization, or surface sync. Debug settings may mask real rendering bugs or create performance regressions if left programmed outside diagnostic/golden-register paths.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include or indirectly depend on `gc_11_5_0_sh_mask.h`, especially GC 11.5.0 VM, GFX, MES/SDMA, reset, KFD, PM, debug, and perf paths.
- Mechanical comparison against AMD's authoritative GC 11.5.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 2579-5025.
- Cross-checks that all 244 register names in this chunk have matching address definitions in `gc_11_5_0_offset.h`.
- Static mask/shift sanity checks: masks should align with shifts, fields for one register should not overlap unless documented, full-width data fields should use `0xFFFFFFFFL`, and repeated low/high/result/status families should have consistent widths.
- SDMA0 tests that program performance counters, clear/enable/disable them, run controlled DMA workloads, read low/high results, and check for monotonic or expected activity.
- GFX idle and reset tests that poll `GRBM_STATUS*`, exercise `GRBM_SOFT_RESET` paths, and verify post-reset engine recovery without impossible busy/clean combinations.
- Hang/debug dump tests that decode GRBM read/write errors, invalid-pipe logs, CP busy/stalled/status registers, CP ring/read pointers, queue thresholds/availability, SQ/SPI active-wave counters, and GDS fault/EDC registers.
- SR-IOV or virtualized-device tests that trigger faults or reset requests and verify VF/VFID/VMID/SSRCID/TMZ attribution in GRBM/GDS/CP-related logs.
- Shader debug tests for SQ watchpoints, trap-screen base/mask/GPR windows, SPI lifetime counters, load-balancer counters, and crawler controls.
- Rendering and conformance tests after any `DB_DEBUG` or depth-buffer debug programming changes, with attention to compression, HiZ/HiS, fast-Z/stencil, z-plane optimization, and depth/HTILE synchronization behavior.
- Runtime warning signals include SDMA0 perf counter nonsense, failed idle waits, GPU reset loops, wrong fault attribution, CP queue stalls, impossible GRBM/CP status dumps, unexpected GDS protection faults, EDC counter spikes, shader trap misrouting, or depth-buffer rendering/performance regressions.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002550`. It covers lines 2579-5025 of `gc_11_5_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to include the immediately preceding SDMA0 decode fields and the remaining `DB_DEBUG` masks after line 5025.

### subset-b-002551: lines 5026-7369

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 5026-7369

## Scope

This chunk is a generated AMD GC 11.5.0 graphics-core register field header. It contains `#define` constants for bit shifts and bit masks, not executable C. The assigned range starts in the middle of the `gc_rbdec` `DB_DEBUG` register definition, continues through depth-buffer, color-buffer, graphics backend, GCEA, SPI, and RMI register blocks, and ends in the middle of `RMI_UTCL1_CNTL1`. The companion offset header (`gc_11_5_0_offset.h`) supplies register addresses; this file supplies the field layouts used by register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD`.

Because this is a generated hardware interface header, the "APIs" are the macro names themselves. The stable convention is:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned bit mask.
- Register names align with `reg*` or `mm*` address symbols in the matching offset header.

## Purpose

The chunk describes how software should pack and unpack register values for several GC subblocks:

- `gc_rbdec`: render backend/depth buffer/color buffer controls, including DB debug and stutter controls, DB FIFO depths, RB redundancy/backend disable mapping, GB address layout, CB hardware controls, CB DCC/cache behavior, and CB memory arbiters.
- `gc_gceadec`, `gc_gceadec2`, `gc_gceadec3`: Graphics Coherent Engine Arbiter and EA/SDP controls. These cover client-to-group mapping, group-to-VC mapping, request combining/flushing, arbitration priority coefficients, burst limits, credit/tag/VC reservation, MAM controls, EDC counters, error status, probe routing, and SDP enable/request control.
- `gc_spipdec2`: SPI queue/event and export throttling controls.
- `gc_rmi_rmidec`: RMI global controls, status, subblock FIFO counters, crossbar configuration, UTC/XNACK controls, demux controls, and the beginning of UTCL1 control fields.

The values are hardware ABI. Driver code must use them exactly as published for GC 11.5.0; a one-bit drift can make register programming target the wrong hardware behavior.

## Important Register Groups

### DB and RB/GB/CB fields

The range begins with the tail of `DB_DEBUG` masks and then defines `DB_DEBUG2` through `DB_DEBUG7`, `DB_DEBUG5`, stutter controls, FIFO-depth registers, and backend topology registers.

Key DB fields include:

- Compression and fast-path debug controls: `DB_DEBUG__DEBUG_FAST_Z_DISABLE_MASK`, `DB_DEBUG__DEBUG_FAST_STENCIL_DISABLE_MASK`, `DB_DEBUG2__ALLOW_COMPZ_BYTE_MASKING_MASK`, `DB_DEBUG3__DISABLE_ZCMP_DIRTY_SUPPRESSION_MASK`, and `DB_DEBUG5__DISABLE_Z_LIMIT_SUMM_MASK`.
- Cache and memory behavior toggles: `DB_DEBUG2__DISABLE_TC_ZRANGE_L0_CACHE_MASK`, `DB_DEBUG2__DISABLE_TC_MASK_L0_CACHE_MASK`, `DB_DEBUG4__DISABLE_MCC_BURST_FIFO_MASK`, `DB_DEBUG4__WR_MEM_BURST_CTL_MASK`, and `DB_FREE_CACHELINES__FREE_Z_ONLY_MASK`.
- Synchronization and hazard behavior: `DB_DEBUG__DISABLE_DEPTH_SURFACE_SYNC_MASK`, `DB_DEBUG__DISABLE_HTILE_SURFACE_SYNC_MASK`, `DB_DEBUG4__DISABLE_PREZ_POSTZ_DTILE_CONFLICT_STALL_MASK`, `DB_DEBUG5__DISABLE_EVENT_INSERTION_AFTER_ZPC_BEFORE_CONTEXT_DONE_MASK`.
- Clock and power controls: `DB_FGCG_SRAMS_CLK_CTRL__OVERRIDE0_MASK` through `OVERRIDE31_MASK`, plus `DB_FGCG_INTERFACES_CLK_CTRL__DB_*_OVERRIDE_MASK`.
- Resource sizing: `DB_FIFO_DEPTH1`, `DB_FIFO_DEPTH2`, `DB_FIFO_DEPTH3`, `DB_FIFO_DEPTH4`, `DB_WATERMARKS`, `DB_MEM_ARB_WATERMARKS`, and `DB_CREDIT_LIMIT`.

Backend topology and address mapping fields include `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, `GB_BACKEND_MAP`, `GB_GPU_ID`, and `CC_RB_DAISY_CHAIN`. These expose the number of pipes, pipe interleave size, compressed fragment limit, number of packers, shader engines, RBs per shader engine, backend disable masks, and RB ordering. These values are commonly used by graphics initialization and memory tiling logic to derive how render backends map to the memory system.

The CB section defines:

- `CB_KEY_OVERRIDE_0` through `CB_KEY_OVERRIDE_7`, all full-register override fields.
- `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, and `CB_HW_CONTROL_4`, covering color-cache fetch policy, SMT scoring, shader/blend optimizations, early write acknowledgements, NACK processing, DCC/VRS/FMAsk options, serializer optimization, and pixel-in-quad handling.
- `CB_DCC_CONFIG` and `CB_DCC_CONFIG2`, covering sample mask tracking, constant encode disable, read-return FIFO depth, DCC cache tag count, and DCC key-disable behavior.
- `CB_HW_MEM_ARBITER_RD` and `CB_HW_MEM_ARBITER_WR`, which define read/write memory arbiter modes, age handling, CC/DC weights, decay behavior, age/weight scaling, and last-beat grouping.
- `CB_CACHE_EVICT_POINTS`, which controls high/low points for CC/DC cache eviction.

### GCEA client mapping, priority, and credit fields

The GCEA span is the largest part of this chunk. It begins at `gc_gceadec` with DRAM read/write client-to-group maps:

- `GCEA_DRAM_RD_CLI2GRP_MAP0/1` and `GCEA_DRAM_WR_CLI2GRP_MAP0/1` assign client IDs `CID0` through `CID31` to 2-bit groups.
- `GCEA_IO_RD_CLI2GRP_MAP0/1` and `GCEA_IO_WR_CLI2GRP_MAP0/1` perform the same mapping for IO paths.
- `GCEA_DRAM_RD_GRP2VC_MAP` and `GCEA_DRAM_WR_GRP2VC_MAP` map request groups to virtual channels.

The arbitration and pacing fields include:

- Lazy/combining controls: `GCEA_DRAM_RD_LAZY`, `GCEA_DRAM_WR_LAZY`, `GCEA_IO_RD_COMBINE_FLUSH`, and `GCEA_IO_WR_COMBINE_FLUSH`.
- CAM controls: `GCEA_DRAM_RD_CAM_CNTL` and `GCEA_DRAM_WR_CAM_CNTL`, including pipe selection, pop-policy, force-on-clash fields, chain limits, and refill-chain enable.
- Burst limits: `GCEA_DRAM_PAGE_BURST` and `GCEA_IO_GROUP_BURST`.
- Priority inputs: `GCEA_*_PRI_AGE`, `GCEA_*_PRI_QUEUING`, `GCEA_*_PRI_FIXED`, `GCEA_*_PRI_URGENCY`, and `GCEA_*_PRI_QUANT_PRI1/2/3`.
- Urgency masking: `GCEA_IO_RD_PRI_URGENCY_MASKING` and `GCEA_IO_WR_PRI_URGENCY_MASKING`, which provide mask-enable/mask-value pairs for many request classes such as SDMA, CP, CB, DB, TCP, SQC, and semaphores.

The SDP and VC reservation section defines:

- `GCEA_SDP_ARB_DRAM` and `GCEA_SDP_ARB_FINAL` for read/write burst limits, early switch conditions, chain breaking, readonly VCs, error event/halt request behavior, and per-path throttles.
- `GCEA_SDP_DRAM_PRIORITY` and `GCEA_SDP_IO_PRIORITY` for 4-bit read/write group priorities.
- `GCEA_SDP_CREDITS`, `GCEA_SDP_TAG_RESERVE0/1`, `GCEA_SDP_VCC_RESERVE0/1`, and the start of VCD reserve handling around the `gc_gceadec2` boundary.
- `GCEA_SDP_REQ_CNTL` for pass-PW overrides, request-chain overrides, inner domain mode, and block-level fields for read/write/atomic traffic.
- `GCEA_SDP_ENABLE__SDP_ENABLE_MASK`, a simple enable bit near the `gc_gceadec3` section.

The MAM and error-observability fields include:

- `GCEA_MISC` and `GCEA_MISC2`, with relative priority mode bits, early write-return enables per VC, link-manager thresholds, chain-switch behavior, and an `INTERLEAVE_PRI_WITHIN_QUANTUM` control.
- `GCEA_LATENCY_SAMPLING`, which selects sampler paths, operation types, and VCs.
- `GCEA_MAM_CTRL` and `GCEA_MAM_CTRL2`, controlling MAM disable, DBIT/ARAM coalescing, flush tracker operations, SDP priority, ARAM tracking geometry, and forced query-dirty behavior.
- `GCEA_EDC_CNT`, `GCEA_EDC_CNT2`, and `GCEA_EDC_CNT3`, which expose compact 2-bit SEC/DED/SED counters for command, data, page, tag, and MAM memories across DRAM, IO, GMI, read-return, and write-return paths.
- `GCEA_GL2C_XBR_MAXBURST`, `GCEA_PROBE_CNTL`, `GCEA_PROBE_MAP`, and `GCEA_ERR_STATUS`. `GCEA_ERR_STATUS` includes SDP read/write response status bits, dataparity error bits, request-type error bits, error-source fields, and `CLEAR_ERROR_STATUS`.
- `GCEA_RRET_MEM_RESERVE` with read-return tag/VC credit reserve fields.

### SPI fields

The `gc_spipdec2` section is small:

- `SPI_PQEV_CTRL` has `NUM_QUEUES` and `PQEV_ENABLE` fields.
- `SPI_EXP_THROTTLE_CTRL` controls export throttling with enable, period, upstep/downstep, low/high stall monitor history counts, stall threshold, skew count, and throttle reset.

These fields sit in the shader processor/input side of graphics scheduling and export pacing. They are likely programmed by GPU initialization tables or firmware-assisted paths, not ordinary hot-path drawing code.

### RMI fields

The `gc_rmi_rmidec` section defines RMI control and status:

- `RMI_GENERAL_CNTL` exposes burst disable, VMID bypass enable bitmap, RB0 harvest enable, and loopback-disable-by-request-type fields.
- `RMI_GENERAL_CNTL1` controls early write acknowledgements per memory type, 64-byte read stall modes for two TCIW paths, loopback early-WRACK disable, policy override, arbiter address-change enable, and last-of-burst insertion disable.
- `RMI_GENERAL_STATUS` reports combined RMI errors, skid FIFO over/underflow, crossbar busy, scoreboard busy, TCIW formatter/return formatter busy, read/write consumer FIFO busy, and skid FIFO free-space-zero error.
- `RMI_SUBBLOCK_STATUS0` through `RMI_SUBBLOCK_STATUS3` expose UTC external latency FIFO occupancy/full/empty state, TCIW inflight counters, skid FIFO free space, PRT FIFO usage, and total free space.
- `RMI_XBAR_CONFIG` exposes mux override, request-type override, CB/DB override, arbiter disable, request-enable masks, request override, and RB0 enable.
- `RMI_PROBE_POP_LOGIC_CNTL` controls external latency FIFO depths and translation-combine behavior.
- `RMI_UTC_XNACK_N_MISC_CNTL` controls XNACK timer increment/start values, UTCL1 permission mode, and CP VMID reset request disable.
- `RMI_DEMUX_CNTL` defines demux arbiter override, stall timer, and mode fields for two arbiters.
- `RMI_UTCL1_CNTL1` begins at the end of this chunk. The assigned range covers shifts through `REG_INV_VMID`; the masks and remaining fields continue in the following chunk.

## Control Flow

There is no local control flow. The runtime flow exists in consumers:

1. Code includes `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h`.
2. It reads or builds a 32-bit register value using `RREG32*`/literal defaults.
3. It applies fields with helpers such as `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` or extracts fields with `REG_GET_FIELD(value, REGISTER, FIELD)`.
4. It writes the value with `WREG32*`, or records field metadata through macros such as `SOC15_REG_FIELD`.

The only direct C include of this exact GC 11.5.0 mask header found in this tree is `amdgpu/gfxhub_v11_5_0.c`, which uses this mask-header family for GPUVM/GFXHUB register programming. The DB/CB/GCEA/RMI symbols in this chunk are also consistent with programming patterns in neighboring AMDGPU generations: golden register tables set DB/CB/GCEA defaults, RAS/EDC tables use `GCEA_EDC_CNT*` fields for error counters, and error handlers clear or decode `GCEA_ERR_STATUS`.

## State and Persistence

The macros have no storage. They describe volatile MMIO hardware state:

- DB/CB/RB/GB fields affect render backend behavior, cache policy, compression, synchronization, and topology.
- GCEA fields affect request routing, arbitration, virtual-channel pressure, credits, error reporting, and EDC observability.
- SPI fields affect queue/event and export throttling behavior.
- RMI fields affect RMI request handling, XNACK/UTCL1 behavior, crossbar/demux routing, and status reporting.

Register values normally persist only until GPU reset, mode switch, power-gating reset, suspend/resume, or firmware reinitialization. The driver and firmware may reapply golden settings during ASIC initialization or resume. Some status/counter registers are read-only or write-to-clear by convention, notably status/error/counter style registers such as `RMI_GENERAL_STATUS`, `RMI_SUBBLOCK_STATUS*`, `GCEA_EDC_CNT*`, and `GCEA_ERR_STATUS`.

## Dependencies and Integration Points

Primary dependencies:

- `gc_11_5_0_offset.h`: supplies register addresses that pair with these field masks.
- AMDGPU SOC15 access helpers: `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, and golden-register table helpers.
- Bitfield helpers: `REG_SET_FIELD` and `REG_GET_FIELD`, which depend on the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- Hardware/firmware ABI: generated field names and bit positions must match the GC 11.5.0 register specification and firmware expectations.

Important integration surfaces:

- Graphics initialization and golden settings: DB/CB/GCEA/RMI fields are commonly programmed in generation-specific golden register arrays or IMU/RLC initialization tables.
- GPU memory management: `GB_ADDR_CONFIG*`, RMI UTCL1/XNACK controls, and GCEA routing/priority fields interact with memory tiling, GPUVM behavior, and request flow to memory clients.
- RAS/error reporting: `GCEA_EDC_CNT*`, `GCEA_ERR_STATUS`, and RMI status fields are natural inputs to diagnostics, RAS reporting, and hardware-health telemetry.
- Debug and bring-up: `DB_DEBUG*`, `CB_HW_CONTROL*`, `GCEA_PROBE*`, `SPI_EXP_THROTTLE_CTRL`, and `RMI_*STATUS*` fields are likely used when validating silicon, chasing hangs, or tuning performance.

## Risks

- Bitfield mismatch: incorrect shift or mask values can silently program unrelated bits. This is especially dangerous for full-register fields and dense maps such as `GCEA_*_CLI2GRP_MAP*`, `GCEA_*_PRI_*`, and `DB_FGCG_SRAMS_CLK_CTRL`.
- Reserved-bit writes: many fields include `SPARE`, `RESERVED`, or broad unused masks. Callers should preserve reset values unless the hardware spec says a reserved field is writable.
- Cross-generation reuse: field names recur across GC generations, but masks may differ. Code must include the GC 11.5.0 header when targeting GC 11.5.0 rather than borrowing values from `gc_10_3_0`, `gc_11_0_*`, or GC 12 headers.
- Partial chunk boundaries: this research slice omits the beginning of `DB_DEBUG` and the end of `RMI_UTCL1_CNTL1`. Any merged per-file report should reconcile adjacent chunks before claiming full register coverage.
- Hardware side effects: fields such as flush, clear, force miss, throttle reset, disable clocks, disable caches, or clear error status can have immediate runtime effects. They should not be manipulated from generic debug code without the same sequencing used by the driver/firmware.
- Virtualization/SRIOV: some low-level GC registers may be PF-only or firmware-owned. VF code should avoid direct writes unless the existing access policy explicitly allows them.

## Test Signals

Useful validation signals for changes touching this header or consumers:

- Compile coverage: an AMDGPU build with GC 11.5.0 paths enabled catches renamed, missing, or malformed macros.
- Register helper smoke tests: any consumer using `REG_SET_FIELD`/`REG_GET_FIELD` should produce expected values for representative multi-bit fields such as `GB_ADDR_CONFIG__NUM_PKRS`, `CB_HW_MEM_ARBITER_RD__SCALE_WEIGHT`, `GCEA_SDP_ARB_FINAL__DRAM_BURST_LIMIT`, and `RMI_GENERAL_CNTL__VMID_BYPASS_ENABLE`.
- Boot/init logs on GC 11.5.0 hardware: look for GPUVM initialization success, no early GFXHUB protection faults, and no register access faults.
- Suspend/resume and GPU reset: DB/CB/GCEA/RMI state should be reinitialized cleanly after reset or resume.
- Graphics workload stability: render/depth compression, DCC, blend optimization, and backend mapping changes should be validated with basic rendering, Vulkan/GL CTS subsets, and stress workloads that exercise depth/stencil and color compression.
- Memory/error telemetry: RAS or debug paths should decode `GCEA_EDC_CNT*`, `GCEA_ERR_STATUS`, and `RMI_GENERAL_STATUS` consistently with hardware events; write-to-clear paths should clear only intended bits.
- Performance regressions: arbitration, burst, credit, and throttling fields can change latency or throughput. Compare memory-heavy graphics workloads before and after any consumer changes using these fields.

### subset-b-002552: lines 7370-9764

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 7370-9764

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `_MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, dynamic allocations, locks, callbacks, persistence helpers, or executable branches in this range.

The selected range starts in the tail of `RMI_UTCL1_CNTL1` masks, then covers RMI/UTCL1 controls and status, GC VM shared page-fault and virtual-context aperture registers, GCVM L2 page-table cache and protection-fault controls, ATC L2 and L2 TLB translation-assist registers, per-VMID GCVM context controls for contexts 0-15, and invalidate-engine request/ack/address fields for engines 0-17. It ends at the beginning of `GCVM_INVALIDATE_ENG7_ADDR_RANGE_LO32`; the rest of that address-range family continues in a later chunk.

Although this repository path is under a `ceph-client` mirror, this source is AMDGPU DRM graphics-core hardware metadata, not filesystem implementation.

## Purpose

`gc_11_5_0_sh_mask.h` supplies bit layouts for GC 11.5.0 registers. Driver code pairs these constants with register addresses from the matching GC 11.5.0 offset header and uses common AMDGPU helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to update or decode individual fields without embedding magic bit positions.

This chunk is centered on address translation, cache invalidation, VM fault handling, and VM apertures:

- RMI and UTCL1 controls expose GPUVM response modes, client invalidation controls, LFIFO/cache-depth reductions, write-combine/reorder controls, scoreboard flush tracking, RMI crossbar arbitration, clock controls, RB-to-GLX client-ID mapping, spare/chicken-bit fields, and redundancy settings.
- UTCL1 registers control per-client bypasses, forced range or global invalidation, page-size encodings, cache bank/way hashing, address-log behavior, and busy/XNACK/range-invalidation status.
- GCMC shared page-fault registers describe MMIO/PCI/TOM/FB/system aperture boundaries, default system aperture physical pages, steering, PF/VF virtual reset requests, active VF/VFID reporting, local/system memory aperture policy, local-FB lock control, and UTCL2/L2 clock-gating controls.
- GCVM L2 registers configure page-table cache behavior, protection-fault enable/default policy, dummy-page fault behavior, fault status/address/default-address capture, identity aperture and physical-offset mapping, cache bank/hash/RT-class selection, parity injection/checking, walker throttling, PTE-cache dump access, GCR settings, and credit-safety update hooks.
- ATC L2 and L2TLB registers define ATS/ATC request concurrency, cache invalidation behavior, cache entry dump data, parity status, clock/memory power controls, SDP port clock gating, TLB status, and GPUVA/VMID translation-assist request/response payloads.
- VM context registers repeat the same context-enable, page-table depth/block-size, retry, and fault interrupt/default controls for GCVM contexts 0 through 15, followed by a context-disable bitmap.
- Invalidate-engine registers provide semaphores, per-VMID invalidation requests, flush type, L2 PTE/PDE and L1 PTE invalidation controls, fault-address-clear requests, 4K-only invalidation mode, per-VMID ack bits, semaphore ack bits, and the first range-address low/high fields for engines 0 through 6 plus the start of engine 7.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register field mask.
- Register address symbols live in the companion `gc_11_5_0_offset.h` header, commonly with `mm...` names matching the register.
- AMDGPU callers normally consume these constants through register field helpers, read-modify-write MMIO helpers, debug dumps, VM invalidation code, reset paths, virtualization paths, and fault-handling paths.

Major macro families in this slice are:

- `RMI_UTCL1_CNTL1`, `RMI_UTCL1_CNTL2`, `RMI_UTC_UNIT_CONFIG`, `RMI_TCIW_FORMATTER*`, `RMI_SCOREBOARD_*`, `RMI_XBAR_ARBITER_CONFIG*`, `RMI_CLOCK_CNTRL`, `RMI_UTCL1_STATUS`, `RMI_RB_GLX_CID_MAP`, `RMI_SPARE*`, and `CC_RMI_REDUNDANCY`.
- `UTCL1_CTRL_1`, `UTCL1_HASH_CTRL`, `UTCL1_ALOG`, and `UTCL1_STATUS`, covering UTCL1 bypass/invalidation/page-size/hash/logging/status fields.
- `GCMC_VM_*` and `GCMC_SHARED_*` shared VM/aperture registers, including MMIO base/limit, PCI control, top-of-memory, FB offset, system aperture defaults, cacheable/local memory ranges, local FB ranges, AGP ranges, active function identity, virtual reset request, VA 1TB control, and L1 TLB control.
- `GCVM_L2_*`, `GCVML2_*`, and `GCUTCL2_*` page-table cache, fault, parity, bank selection, walker throttle, PTE cache dump, clock-gating, GCR, and credit-safety fields.
- `GC_ATC_L2_*`, `GCL2TLB_TLB0_STATUS`, and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_*`, covering ATC L2 cache behavior and explicit translation-assist request/response registers.
- `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL` and `GCVM_CONTEXTS_DISABLE`, giving per-context enable/page-table/fault behavior and disable bits.
- `GCVM_INVALIDATE_ENG[0-17]_{SEM,REQ,ACK}` plus `GCVM_INVALIDATE_ENG[0-6]_ADDR_RANGE_{LO32,HI32}` and the beginning of `GCVM_INVALIDATE_ENG7_ADDR_RANGE_LO32`.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in consumers is:

1. Select the GC 11.5.0 register definitions for the active ASIC.
2. Choose the matching register address from `gc_11_5_0_offset.h`.
3. Read a current register value, prepare a register write, or decode a diagnostic/fault/status snapshot.
4. Use the `__SHIFT`/`_MASK` pairs, normally via helper macros, to pack a field value or extract one.
5. Execute the actual MMIO, indirect register access, polling loop, command submission, VM invalidation, debug dump, or recovery sequence in AMDGPU code.

For VM invalidation, higher-level code programs an invalidate engine semaphore/range, writes a request with per-VMID bits and cache-level controls, then polls or observes ack/semaphore state. For VM context setup, code programs page-table depth and fault policies per context and may use the disable bitmap to gate contexts. For protection faults, runtime code reads status and address registers, decodes VMID/client/perms/source/default behavior, may clear captured fault address state through invalidate request bits, and reports or recovers at the VM/KFD/AMDGPU layers. For UTCL1/GCVM/ATC cache controls, the actual ordering, drain, poll, timeout, and reset rules are not encoded here.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU registers whose state is owned by hardware, firmware, and AMDGPU runtime programming.

RMI, UTCL1, GCVM L2, ATC L2, and aperture controls are persistent hardware configuration until changed, reset, lost through power transitions, or restored during resume/GPU reset. Many fields affect global address translation behavior: bypasses, page-size encodings, cache invalidation policy, cache fragment sizes, bank/hash selection, clock-gating overrides, walker throttles, and local/system/FB aperture boundaries. Incorrect values can persistently change translation correctness or performance across all clients using those paths.

Fault/status registers are mostly live or sticky hardware state. `GCVM_L2_PROTECTION_FAULT_STATUS` exposes fault attribution and access type fields, while address/default-address registers hold captured or programmed page information. `UTCL1_STATUS`, `GCVM_L2_STATUS`, `GC_ATC_L2_STATUS`, `GC_ATC_L2_STATUS2`, and `GCL2TLB_TLB0_STATUS` can change asynchronously with memory traffic, invalidations, parity events, and faults. The header does not express read-only, sticky, write-one-to-clear, self-clearing, or clear-on-read semantics.

`GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL` represent persistent per-VMID/context policy for page-table depth, block size, retry behavior, and whether specific protection faults interrupt or resolve to default pages. These settings directly shape how GPU VM faults are surfaced to the kernel, KFD, or userspace workloads.

Invalidate-engine registers represent short-lived synchronization and cache maintenance state. Semaphore, request, ack, and range-address fields must be coordinated with hardware sequencing. Per-VMID invalidation bitmaps cover up to 16 VMIDs per engine; request fields select flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, optional fault-address clear, and 4K-only invalidation. Ack bits and range-address fields are hardware-owned during invalidation and should not be treated as ordinary persistent configuration.

Reserved and spare fields appear throughout the range. Callers should preserve undocumented bits during read-modify-write unless a golden setting or hardware workaround explicitly documents a full-register value.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register family remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` provides matching register addresses.
- Any generated GC 11.5.0 default/header metadata must agree with these bit assignments where reset values or enumerations exist.
- AMDGPU VM, MM hub/GMC-adjacent code, GFX initialization, KFD/compute memory management, SR-IOV/virtualization, interrupt/fault handling, reset, suspend/resume, debugfs, and hang-dump paths can rely on these definitions.

Important integration points include VM context creation and teardown, GPUVM page-table setup, invalidation after PTE/PDE updates, VM fault reporting and recovery, dummy/default page behavior, cache/TLB parity diagnostics, address-range invalidation, ATS/ATC translation assistance, SR-IOV active function and virtual reset handling, local/system/FB aperture setup, clock/power gating golden settings, and low-level debug dump decoding.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but can set the wrong hardware bit, corrupt VM context policy, or misdecode a protection fault.
- The chunk boundaries are artificial. It starts after the `RMI_UTCL1_CNTL1` shifts and ends before the complete invalidate-engine range-address family, so adjacent chunks are needed for full register-family context.
- VM context controls are repeated 16 times. A generator or copy/paste mismatch affecting one `GCVM_CONTEXTn_CNTL` register could produce failures isolated to a subset of VMIDs or queues.
- Invalidate engines 0-17 are highly repetitive and sequencing-sensitive. Incorrect per-engine request, ack, or semaphore masks can make invalidations appear complete while stale PTE/PDE/TLB entries remain visible.
- Address fields are unit- and alignment-sensitive. Aperture, FB, AGP, default physical page, identity aperture, translation-assist, fault-address, and range-address fields are not necessarily raw byte addresses despite full-width-looking masks.
- Fault policy bits are security and correctness sensitive. Misprogramming interrupt/default handling for range, dummy page, PDE0, valid, read, write, or execute faults can hide real faults, over-report recoverable faults, or allow accesses to resolve through default pages unexpectedly.
- Virtualization fields such as PF/VF reset requests, active VF/VFID, request VMID/VFID/VF, client ID, and fault attribution must be decoded exactly for SR-IOV isolation and diagnostics.
- Clock-gating, credit-safety, walker-throttle, cache-fragment, bank-select, parity-injection, and spare/chicken-bit fields can cause performance cliffs or rare hangs if altered outside documented golden settings.
- Live status and counter-like fields can race with in-flight memory traffic. Polling code must use documented drains, timeouts, and stable-snapshot rules.
- The macros cannot encode access permissions. Full-width `DATA`, `ADDR`, or `STATUS` masks do not imply that arbitrary writes are valid or that readback is stable.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime VM testing:

- Kernel build coverage for AMDGPU files that include `gc_11_5_0_sh_mask.h` with the matching GC 11.5.0 offset header.
- Mechanical comparison against AMD's authoritative GC 11.5.0 register database for every shift/mask pair in this range.
- Static sanity checks that masks align with shifts, fields in each register do not overlap except documented aliases/reserved areas, all register names have matching address definitions, and repeated families remain structurally identical where expected.
- VM invalidation tests that update PTEs/PDEs, issue per-VMID and range invalidations through multiple invalidate engines, poll ack/semaphore bits, and verify stale mappings are not observed.
- GPUVM fault tests for invalid, read, write, execute, range, dummy-page, and PDE faults, checking interrupt/default-page behavior and decoded `GCVM_L2_PROTECTION_FAULT_STATUS` attribution.
- Context tests across VMIDs 0-15 to confirm page-table depth, block size, retry behavior, context disable bits, and per-context fault policy behave consistently.
- Suspend/resume and GPU reset tests that verify VM aperture, GCVM L2, UTCL1, ATC L2, and invalidate-engine state is reprogrammed or cleared as expected.
- SR-IOV/virtualization tests that trigger PF/VF reset requests, active-function changes, VM faults, and translation-assist operations, then validate VF/VFID/VMID/client attribution.
- ATC/ATS and translation-assist tests that exercise request/response fields, permissions, fragment size, TMZ, NACK/ACK, and no-PTE paths.
- Debug/hang-dump tests that verify UTCL1, GCVM L2, ATC L2, L2TLB, scoreboard, and protection-fault status fields decode coherently under memory traffic and fault injection.
- Regression signals include unexplained VM faults, stale mappings after invalidation, GPUVM page-table update races, KFD process eviction/restore failures, SR-IOV attribution errors, parity/fault status that cannot be cleared, translation-assist timeouts, or GPU reset loops near VM/cache invalidation paths.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002552`. It covers lines 7370-9764 of `gc_11_5_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `RMI_UTCL1_CNTL1` and `GCVM_INVALIDATE_ENG7_ADDR_RANGE_LO32` families and to place the VM/invalidation metadata in the full GC 11.5.0 register map.

### subset-b-002553: lines 9765-12372

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 9765-12372

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the middle of the GCVM invalidation-engine address-range family, with the `GCVM_INVALIDATE_ENG7_ADDR_RANGE_LO32` masks visible before the matching `HI32` comment. The chunk then covers GCVM page-table base/start/end address fields for contexts 0 through 15, GCVM L2 per-PF/VF PTE cache fragment sizing, GCVM/GCMC/GCUTCL2/ATC/GCL2TLB performance counters and selector/control registers, GCVM ATS/IOMMU/translation-fault controls, shader-stage register fields for PS/GS/HS/ES/LS, compute dispatch and compute resource registers, and the beginning of CP command-processor public/decode fields. The slice ends after `CP_ECC_FIRSTOCCURRENCE__VMID_MASK`; the obsolete ring-specific ECC first-occurrence macros and following GB EDC fields continue in the next adjacent chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 11.5.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_11_5_0_sh_mask.h` supplies the bit layouts for GC 11.5.0 registers. Driver code pairs these macros with register addresses from the matching `gc_11_5_0_offset.h` header and, where available, generated reset/default values. Consumers normally use the constants through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` so register fields can be packed or extracted without hard-coded bit positions.

This chunk focuses on virtual memory programming, shader/compute launch state, and CP queue/interrupt controls:

- GCVM invalidation range fields for engines 7 through 17, with split low/high logical page-address fields and an `S_BIT` flag in each low word.
- Per-context GCVM page-table base, start, and end address fields for contexts 0 through 15, plus per-PF/VF PTE cache fragment-size knobs.
- L2/ATC/TLB performance counter result, selection, mode, and configuration registers for GCVM, GCMC VM L2, GCUTCL2, GC ATC L2, and GCL2TLB blocks.
- ATS, IOMMU host-translation enable/control/optimization, translation fault control, GPUVA VMID translation assist, and UTCL2 translation-bypass controls.
- Shader program address/resource/checksum/user-data/request-control/accumulator fields for pixel shader, geometry shader, hull shader, and related ES/LS pairing registers.
- Compute dispatch dimensions, start/restart coordinates, thread counts, pipeline/perf enable, program addresses/resources, VMID, destination/static-thread controls, temporary ring sizing, wave relaunch/restore, dispatch tunnel/end, and user data.
- CP command-processor queue, doorbell, priority, VMID, interrupt, UTCL1, virtualization, ring pointer, power, fatal/error, and ECC first-occurrence fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion offset header, commonly with `mm...` names matching these register names.
- AMDGPU callers normally access these fields through `REG_SET_FIELD`, `REG_GET_FIELD`, read-modify-write MMIO helpers, command-packet register programming, debugfs/perf tooling, reset paths, virtualization handling, and shader/compute queue setup.

The main macro families in this slice are:

- `GCVM_INVALIDATE_ENG7..17_ADDR_RANGE_{LO32,HI32}`: page-range invalidation address encodings. Low words expose `S_BIT` and low logical page address bits; high words expose the high logical page address bits.
- `GCVM_CONTEXT0..15_PAGE_TABLE_{BASE,START,END}_ADDR_{LO32,HI32}`: per-VMID/context page-table directory base and valid logical page-number bounds. Base addresses use full low/high PDE fields; start/end high words use four high logical page-number bits.
- `GCVM_L2*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`: base and per-context L2 PTE cache fragment-size fields for system and local memory fragment sizes.
- `GCVML2_PERFCOUNTER2_*`, `GCMC_VM_L2_PERFCOUNTER*`, `GCUTCL2_PERFCOUNTER*`, `GC_ATC_L2_PERFCOUNTER*`, and `GCL2TLB_PERFCOUNTER*`: performance counter low/high results, event selectors, selector extensions, mode controls, per-counter configs, result selection, clear, and enable controls.
- `GCVM_PCIE_ATS_CNTL`, `GCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `GCVM_IOMMU_*`, `GCUTC_TRANSLATION_FAULT_CNTL*`, and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`: translation and IOMMU controls for ATS, host translation enablement, optimization, fault-response behavior, VMID bypass masks, and GPU virtual-address assist behavior.
- `SPI_SHADER_*`: shader stage program registers for PS, GS, and HS plus ES/GS and LS/HS pair addresses. Resource fields include VGPR/SGPR counts, priority, float mode, DX10 clamp, debug mode, scratch enable, user SGPR counts, trap/debug flags, LDS sizing, CU enable, wave limit, and stage-specific controls such as meshlet dimensions.
- `COMPUTE_*`: compute dispatch state. These macros cover dispatch dimensions and starts, threadgroup sizes, program address and resource descriptors, VMID, resource limits, per-SE destination/static-thread controls through SE7, temporary ring size, relaunch controls, wave restore address, dispatch packet/scratch addresses, DDID, shader checksum, tunnel/end markers, and 16 user-data registers.
- `CP_*`, `CPG_*`, `CPC_*`, and `CPF_*`: command-processor public/decode controls for CU masks, EOP wait timing, MGCG sync, interrupt metadata, virtualization status, UTCL1 controls/errors, AQL status, ring-buffer bases/control/read/write pointers, doorbell ranges, priorities, VMIDs, process quantum, fatal/GFX error attribution, interrupt enable/status for generic and ring-specific paths, power clock-halt bits, and ECC first-occurrence attribution.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 11.5.0 register header for the active ASIC generation.
2. Choose the matching register address from `gc_11_5_0_offset.h`.
3. Read an existing register value, prepare an indexed-register/debug/perf access, or construct an MMIO/command-packet register write.
4. Use the `__SHIFT`/`__MASK` pairs, usually through generated register helpers, to pack a field value or extract status bits.
5. Feed the resulting value into VM setup, TLB invalidation, IOMMU/ATS programming, shader or compute pipeline setup, CP ring setup, interrupt handling, virtualization, perf counter programming, hang diagnostics, reset, or power-management logic.

For GCVM context registers, driver VM setup programs page-table base and address bounds before GPU work uses a VMID, and invalidation code writes address-range fields before triggering per-engine TLB/cache invalidation. For performance counters, consumers select events and modes, configure counter routing, clear/enable accumulation, then read low/high result words. Shader and compute register flows are usually populated by command-stream packets or queue setup paths immediately before dispatch/draw work. CP register flows initialize rings and doorbells, update pointers, program priority/VMID/quantum state, enable interrupts, and inspect status/error/ECC state during interrupt, debug, or recovery handling.

This header does not encode ordering requirements, polling loops, latching sequences, clear-on-read behavior, or reset sequencing; those rules live in AMDGPU engine code, firmware interfaces, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

GCVM context page-table base/start/end registers are persistent VM context state until explicitly reprogrammed, evicted, reset, or lost through power transitions. Incorrect field packing can point a VMID at the wrong page directory or expose the wrong logical address range, causing memory faults, data corruption, or isolation failures. Invalidation address-range registers are transient control state used around TLB/cache invalidation operations, but stale or mispacked ranges can leave translations cached when callers expect them to be invalidated.

ATS/IOMMU/translation-fault controls affect memory translation and fault behavior globally or per VMID. Bypass masks and host-translation enable bits are high risk because they can change which transactions use GPU page tables, IOMMU translation, or fault-assist paths. Translation-fault controls may be sticky or policy-like hardware state; callers must preserve reserved bits and follow documented clear/acknowledge sequences outside this header.

Shader and compute registers are active pipeline/dispatch state. Program address, resource, user-data, scratch, temporary-ring, wave-restore, relaunch, and static-thread-management fields can remain live across dispatches, preemption, suspend/resume, or debug capture until overwritten by the command processor or reset. Bad masks in these fields can launch the wrong shader address, allocate invalid VGPR/SGPR/LDS resources, assign work to the wrong shader engines, or corrupt wave relaunch/restore.

CP ring and doorbell fields persist as queue execution state. Ring base/control, read/write pointer addresses and values, buffer-size masks, VMID/priority/quantum, doorbell ranges, interrupt enables, and UTCL1 controls must match the queue and process being scheduled. Error, fatal, interrupt-status, GFX-error, and ECC first-occurrence registers are live or sticky diagnostic state and may require hardware-defined clearing. `CP_PWR_CNTL` clock-halt fields have direct power/clock side effects and should not be treated as passive status bits.

Performance counter selector/configuration registers persist while counters accumulate. Low/high result registers may require a hardware-specific snapshot or read ordering to avoid torn values; the shift/mask header only describes bit positions and cannot express atomicity, overflow, or latching behavior.

Reserved and obsolete fields appear in this generated area. Callers should preserve reserved bits during read-modify-write unless a documented full-register write is required, especially around VM/IOMMU, shader resource, CP power, and error/interrupt registers.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_default.h`, when present in the same generated register family, provides default/reset values for many registers.
- Common AMDGPU register helpers provide field packing/extraction and MMIO or command-packet access mechanisms.
- AMDGPU VM, GFX, CP, KFD/compute, shader setup, performance counter, reset, suspend/resume, SR-IOV/virtualization, debugfs, and hang-dump paths rely on these bit assignments.

Integration points include VMID/page-table setup, range-based GCVM invalidation, ATS/IOMMU enablement and translation-fault policy, per-VMID bypass/assist handling, graphics pipeline shader register programming, compute queue and dispatch packet setup, wave relaunch after preemption or recovery, CP ring creation and teardown, doorbell mapping, interrupt enable/status handling, priority/quantum scheduling, UTCL1 error handling, virtualization status/fault attribution, power/clock control, performance monitoring, and ECC/fatal-error diagnostics.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bits or decode misleading diagnostics.
- This chunk starts and ends mid-family. It begins after the `GCVM_INVALIDATE_ENG7_ADDR_RANGE_LO32` comment and ends before the ring-specific `CP_ECC_FIRSTOCCURRENCE_*` and following GB EDC fields; file-level conclusions must be merged with adjacent chunks.
- Context macros are repeated across VM contexts 0 through 15. Generator mistakes can affect only one context, producing VMID-specific faults that are difficult to diagnose.
- Split address fields are easy to misuse. Page-table, invalidation, shader program, dispatch-packet, scratch, read-pointer, CU-mask, and wave-restore addresses must be shifted/aligned according to their field definitions, not treated as always-full byte addresses.
- GCVM/IOMMU/ATS/bypass controls affect memory isolation and fault behavior. Incorrect masks can hide faults, bypass translation unexpectedly, or attribute translation failures to the wrong VMID.
- Shader and compute resource fields are densely packed. Incorrect widths for VGPR/SGPR counts, LDS size, scratch enable, CU enables, wave limits, or thread dimensions can cause invalid dispatches, hangs, or silent performance/debug errors.
- CP ring/doorbell/pointer fields are queue-critical. Bad buffer-size masks, pointer address fields, doorbell ranges, VMIDs, priorities, or quantum fields can cause lost work, wrong-process execution, stalled queues, or interrupt storms.
- Interrupt enable/status families are similar but not identical between generic CP and ring0/ring1 variants. Assuming symmetry can miss ring-specific fields or enable unsupported bits.
- `CP_PWR_CNTL`, fatal/error, virtualization, and UTCL1 controls have side effects or sticky state. Full-register writes that do not preserve reserved bits may change undocumented engine behavior.
- Counter result high/low registers can be race-prone if read without the documented latching sequence. This header cannot describe atomic snapshot requirements.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_11_5_0_sh_mask.h`, especially GC 11.5.0 VM, GFX, CP, KFD/compute, reset, virtualization, debug, and perf counter paths.
- Mechanical comparison against AMD's authoritative GC 11.5.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that all registers in this chunk have matching address macros in `gc_11_5_0_offset.h` and expected defaults in the matching default header where generated.
- Static mask/shift sanity checks: masks should align with shifts, full-width data fields should use `0xFFFFFFFFL`, repeated context and user-data families should remain structurally aligned, and bitmap fields should not overlap unless documented.
- VM tests that create multiple VMIDs, program page-table base/start/end bounds, run range invalidations through engines 7 through 17, and verify no stale translations remain after mapping changes.
- IOMMU/ATS/fault tests that exercise host translation enablement, bypass-by-VMID, GPUVA VMID assist, and translation fault control paths with expected VMID and fault attribution.
- Graphics and compute dispatch tests that validate shader program/resource/user-data setup, compute thread dimensions, scratch/temporary ring programming, static-thread-management fields, and wave relaunch/restore after preemption or reset.
- CP ring tests covering ring base/control programming, read/write pointers, write-pointer high words, buffer-size masks, doorbell ranges, priorities, VMIDs, process quantum, and interrupt enable/status behavior for generic, ring0, and ring1 paths.
- Perf counter tests that select GCVM/GCMC/GCUTCL2/ATC/GCL2TLB events, clear/enable counters, read low/high results, and compare monotonicity or expected activity under controlled memory and dispatch workloads.
- Hang/debug dump tests that verify CP GFX/fatal error attribution, UTCL1 errors, virtualization status, interrupt metadata, power/clock-halt state, and ECC first-occurrence fields decode coherently.
- Runtime warning signals include VM faults after valid mappings, stale translations after invalidation, shader launch failures, compute hangs, invalid wave restore, lost doorbell updates, incorrect CP interrupts, misleading perf counters, unexpected UTCL/IOMMU faults, wrong VF/VMID attribution, and GPU reset loops.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002553`. It covers lines 9765-12372 of `gc_11_5_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial GCVM invalidation and CP ECC/GB EDC families and to place these GCVM, shader/compute, and CP definitions in the full GC 11.5.0 register map.

### subset-b-002554: lines 12373-14858

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 12373-14858

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header slice. It contains only C preprocessor `#define` constants for register bit positions and masks. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, or executable branches in this range.

The requested lines contain 2,158 `#define` statements: 1,079 `__SHIFT` macros and 1,079 `_MASK` macros. The range starts in the middle of `CP_ECC_FIRSTOCCURRENCE`, continues through command-processor and compute/graphics queue register fields, crosses into SPI scheduling/debug fields, then into CP HQD queue fields, TCP watchpoint fields, and GDS VMID/GWS/OA resource fields. It ends inside `GDS_OA_VMID3`, before the rest of the per-VMID OA masks and later GDS reset fields.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_11_5_0_sh_mask.h` describes the bit layout of GC 11.5.0 registers. Driver code pairs these field macros with register offsets from `gc_11_5_0_offset.h` and uses AMDGPU helper macros to compose and decode 32-bit hardware register values without open-coded bit numbers.

This chunk covers five main surfaces:

- Command processor reliability, interrupt, queue scheduling, suspend/resume, DDID, graphics HQD, DMA watchpoint, timestamp, UTCL1 status, soft reset, and security-domain controls in the `gc_cppdec` area.
- SPI arbitration, work-conserving launch percentages, per-VMID shader debug/trap controls, compute queue reset, and compute wavefront context-save controls in the `gc_spipdec` area.
- Compute HQD/MQD state in the `gc_cpphqddec` area, including MQD/HQD base addresses, VMID/VQID, queue priorities, quantum, PQ/IB/EOP rings, doorbells, timers, dequeue/offload/semaphore/atomic controls, scheduler/status registers, context-save sizing, GDS resource state, error reporting, AQL control, and DDID counters.
- TCP watchpoint programming in the `gc_tcpdec` area, with four watch address/control slots and VMID/mode/valid fields.
- GDS per-VMID partitioning in the `gc_gdspdec` area, covering `GDS_VMID0..15_BASE`, `GDS_VMID0..15_SIZE`, `GDS_GWS_VMID0..15`, and the beginning of `GDS_OA_VMID0..3`.

## Important APIs, Types, And Macros

The only interface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's in-register bit mask.
- `//<REGISTER>` comments mark generated register boundaries.
- `// addressBlock: ...` comments mark transitions between generated address blocks.

There are no callable APIs or C types here. Consumers normally use these constants through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_FIELD15`.

Important command-processor families in this chunk include:

- Reliability and debug fields: the tail of `CP_ECC_FIRSTOCCURRENCE`, obsolete ring first-occurrence registers, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, and `CP_CPC_DEBUG`.
- Queue write-pointer polling: `CP_PQ_WPTR_POLL_CNTL` and `CP_PQ_WPTR_POLL_CNTL1`, including poll period, one-shot behavior, active status, enable bit, and queue mask.
- Repeated ME pipe interrupt controls and statuses: `CP_ME1_PIPE0..3_INT_CNTL`, `CP_ME2_PIPE0..3_INT_CNTL`, `CP_ME1_PIPE0..3_INT_STATUS`, and `CP_ME2_PIPE0..3_INT_STATUS`. These share fields for compare-query status, dequeue request, CP ECC, SUA violation, GPF, WRM poll timeout, privileged register, opcode error, timestamp, reserved-bit error, and generic interrupt sources.
- Scheduling and context controls: `CP_GFX_QUEUE_INDEX`, per-ME pipe priority counters and priorities, program-counter and interrupt-routine start registers for PFP/ME/MEC, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_IQ_WAIT_TIME1..3`, `CP_RB0_BASE_HI`, `CP_RB1_BASE_HI`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, and `CP_VMID_STATUS`.
- CPC interrupt and suspend fields: `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CPC_INT_CNTX_ID`, `CPC_SUSPEND_CTX_SAVE_*`, `CPC_SUSPEND_CNTL_STACK_*`, `CPC_SUSPEND_WG_STATE_OFFSET`, `CPC_OS_PIPES`, `CP_SUSPEND_RESUME_REQ`, and `CP_SUSPEND_CNTL`.
- DDID and graphics HQD state: `CPC_DDID_*`, `CP_DDID_*`, `CP_GFX_DDID_*`, `CP_GFX_HPD_*`, `CP_GFX_MQD_*`, `CP_GFX_HQD_*`, `CP_RB_WPTR_POLL_ADDR_*`, and `CP_RB_DOORBELL_CONTROL`.
- CP DMA/watch and misc diagnostics: `CP_DMA_WATCH0..3_*`, `CP_DMA_WATCH_STAT*`, `CP_PFP_JT_STAT`, `CP_MEC_JT_STAT`, busy hysteresis registers, `CP_RB_DOORBELL_CLEAR`, ring active/status registers, RCIU CAM data, GPU timestamp offset, SDMA completion/request fields, `CPF_GCR_CNTL`, `CPG_UTCL1_STATUS`, `CPC_UTCL1_STATUS`, `CPF_UTCL1_STATUS`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL`.

Important SPI families include:

- `SPI_ARB_PRIORITY` and `SPI_ARB_CYCLES_0/1`, which define time-slice ordering and duration fields.
- `SPI_WCL_PIPE_PERCENT_GFX`, `SPI_WCL_PIPE_PERCENT_HP3D`, and `SPI_WCL_PIPE_PERCENT_CS0..7`, which provide launch/work allocation percentage fields for graphics, HP3D, and compute pipes.
- `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, and `SPI_COMPUTE_WF_CTX_SAVE`, which drive per-VMID accumulation, shader debug/trap mode, compute queue reset, and wavefront context-save initiation/status.

Important compute HQD/MQD families include:

- Queue identity and lifecycle: `CP_MQD_BASE_ADDR*`, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PIPE_PRIORITY`, `CP_HQD_QUEUE_PRIORITY`, `CP_HQD_QUANTUM`, `CP_MQD_CONTROL`, and dequeue status/request registers.
- Packet queue and doorbell state: `CP_HQD_PQ_BASE*`, `CP_HQD_PQ_RPTR`, read-pointer report addresses, write-pointer poll addresses, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_HQD_PQ_CONTROL`, and `CP_HQD_PQ_WPTR_LO/HI`.
- Indirect buffer, instruction queue, and offload/semaphore controls: `CP_HQD_IB_*`, `CP_HQD_IQ_TIMER`, `CP_HQD_IQ_RPTR`, `CP_HQD_DMA_OFFLOAD`, `CP_HQD_OFFLOAD`, `CP_HQD_SEMA_CMD`, `CP_HQD_MSG_TYPE`, and atomic pre-operation registers.
- Scheduler, status, EOP, and save/restore state: `CP_HQD_HQ_SCHEDULER0/1`, `CP_HQD_HQ_STATUS0/1`, `CP_HQD_HQ_CONTROL0/1`, `CP_HQD_EOP_*`, `CP_HQD_CTX_SAVE_*`, `CP_HQD_CNTL_STACK_*`, `CP_HQD_WG_STATE_OFFSET`, suspend stack/workgroup offsets, and `CP_HQD_CTX_SAVE_SIZE`.
- GDS and error fields: `CP_HQD_GDS_RESOURCE_STATE`, `CP_HQD_ERROR`, `CP_HQD_AQL_CONTROL`, and `CP_HQD_DDID_*`.

Important watchpoint and GDS families include:

- `TCP_WATCH0..3_ADDR_H`, `TCP_WATCH0..3_ADDR_L`, and `TCP_WATCH0..3_CNTL`, which encode address, mask, VMID, mode, and valid bits for TCP-level watchpoints.
- `GDS_VMID0..15_BASE` and `GDS_VMID0..15_SIZE`, which partition GDS address space per VMID.
- `GDS_GWS_VMID0..15`, which partition global wave sync resources per VMID.
- `GDS_OA_VMID0..3`, which begin the per-VMID ordered-append resource mask series continued in the next chunk.

## Control Flow

This header has no runtime control flow. It affects runtime behavior only when C code expands these macros while composing or decoding register values.

The typical implied flow is:

1. Driver code selects a GC 11.5.0 register offset from the companion offset header.
2. It reads, writes, or read-modify-writes a 32-bit register through AMDGPU SOC15 MMIO helpers.
3. It uses a `__SHIFT` and `_MASK` pair, often through `REG_SET_FIELD` or `REG_GET_FIELD`, to isolate the intended field.
4. GPU hardware command-processor, SPI, HQD, TCP, GDS, VM, interrupt, trap, reset, or context-save state machines execute the real operation.

For CP/CPC/ME interrupt handling, higher-level code enables specific interrupt sources, reads corresponding status registers, attributes the event to a pipe/queue/VMID/context/PASID when supported, and clears or masks the source using register-specific semantics. This header defines field locations only; it does not specify clear-on-read, write-one-to-clear, self-clearing, or ordering rules.

For HQD/MQD queue setup, runtime code programs MQD bases, VMID/VQID, queue priority/quantum, packet queue base and size, read/write-pointer report and poll addresses, doorbell offset and enable, IB/EOP rings, context-save memory, and control bits before activating a queue. Dequeue, suspend, preemption, EOP, DDID, and relaunch-related fields are interpreted by firmware and hardware queue schedulers.

For SPI debug, KFD/debug paths program `SPI_GDBG_PER_VMID_CNTL` to enable traps, exception masks, launch modes, and trap-on-start/end behavior for a target VMID. For GDS and TCP watchpoints, runtime code writes per-VMID resource slices or watch slots; the actual access checks occur in hardware.

## State And Persistence Behavior

The macros are stateless compile-time constants. Persistent and volatile state exists only in GPU registers, firmware-managed queue objects, ring buffers, doorbell pages, writeback memory, context-save memory, debug/watchpoint state, and GDS resource allocation.

Hardware state described by the CP/CPC portion includes interrupt enables and latched statuses, ECC/EDC first-fault metadata, queue polling configuration, priority and wait timers, VMID reset/preempt state, suspend context-save addresses and sizes, DDID buffers/counters, HPD/HQD/MQD queue state, ring doorbell controls, DMA watchpoints, timestamp offsets, UTCL1 status bits, security-domain enables, and soft-reset controls. Some fields are configuration, some are live status, some are hardware-updated pointers/counters, and some are command bits with side effects.

Hardware state described by the SPI portion includes arbitration timing, launch/work allocation percentages, per-VMID trap and exception behavior, compute queue reset request state, and wavefront context-save busy/done state.

Hardware state described by the HQD portion includes active/busy state, queue VMID/VQID, priority and quantum, persistent state flags, PQ/IB/EOP ring bases and pointers, doorbell state, scheduler/status words, context-save layout, GDS resource ownership, AQL control, DDID counters, and dequeue/suspend state. These values normally persist until queue teardown, preemption, suspend/resume, reset, firmware reinitialization, or explicit reprogramming.

Hardware state described by the TCP/GDS portion includes watchpoint address/mask/VMID/mode/valid configuration and per-VMID GDS/GWS/OA resource partitions. GDS partition state is process/VMID-visible and must be reset or reallocated carefully when VMIDs are reused.

Reserved or unused fields appear in many registers. Consumers should preserve them during read-modify-write unless the hardware sequence explicitly requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` supplies matching register offsets.
- This tree does not contain a `gc_11_5_0_default.h`; GC 11.5.0 users that need reset values must use local defaults or other generation-specific sources.
- AMDGPU helper macros in the surrounding DRM code provide the bitfield operations and MMIO access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c` directly includes this shift/mask header and its offset header. Within the examined direct consumer, the visible use of this chunk is `CP_DEBUG__CPG_UTCL1_ERROR_HALT_DISABLE` during gfxhub initialization; many other fields in this chunk are part of the same generated ABI for queue, SPI, TCP, and GDS code paths.
- Shared field names are also used by other GC 11-era files such as `gfx_v11_0.c`, `mes_v11_0.c`, and `amdgpu_amdkfd_gfx_v11.c` against their selected offset/header mappings. Those files are useful behavioral references, but they do not directly include the GC 11.5.0 header pair in this tree.

Runtime integration points include VM/gfxhub setup, command-processor interrupt handling, KFD compute queue and MES/HQD programming, graphics queue setup, shader debug/trap control, suspend/resume and preemption, queue reset/relaunch, doorbell submission, ring writeback, DDID tracking, TCP watchpoint debugging, GDS/GWS/OA allocation, ECC/EDC reporting, and GPU reset/hang diagnosis.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong shift or mask can compile cleanly while setting, clearing, or decoding the wrong hardware bit.
- This work item starts and ends inside register groups. The previous chunk owns the beginning of `CP_ECC_FIRSTOCCURRENCE`; this chunk begins at `CP_ECC_FIRSTOCCURRENCE__VMID_MASK`. The next chunk continues `GDS_OA_VMID3` and the remaining GDS OA/reset definitions.
- Repeated register families are easy to update inconsistently. ME1/ME2 pipe interrupt controls/statuses, `CP_DMA_WATCH0..3`, `TCP_WATCH0..3`, `GDS_VMID0..15`, `GDS_GWS_VMID0..15`, and GDS OA per-VMID masks should be mechanically compared for intended symmetry.
- CP/HQD queue fields are liveness-critical. Incorrect queue size, block size, read/write pointer, doorbell, cache policy, VMID/VQID, EXE-disable, privilege, or KMD queue fields can cause lost submissions, stuck fences, bad queue ownership, or hangs.
- Interrupt and status fields can be latched, masked, clear-sensitive, or hardware-updated. Using a status mask as an enable mask, or vice versa, can hide faults or create interrupt storms.
- Suspend, context-save, preemption, and dequeue fields interact with firmware-owned state. Wrong offsets, sizes, policy bits, or request/status decoding can resume queues with corrupt state or fail to quiesce active work.
- `SPI_GDBG_PER_VMID_CNTL` is debugger- and trap-sensitive. Bad exception masks, trap-on-start/end bits, launch modes, or stale VMID selection can trap the wrong process or miss debug events.
- TCP watchpoint and CP DMA watchpoint fields are address-alignment sensitive. Low-address bits are reserved or omitted, so consumers must supply aligned addresses and correct masks.
- GDS/GWS/OA fields are resource-partitioning and isolation-sensitive. VMID reuse, partial reset, or incorrect base/size/mask programming can leak or deny resources across processes.
- Security-domain, soft-reset, and UTCL1 status/error fields should not be treated as ordinary data fields. Full-register writes can reset active domains, drop diagnostics, or change fault handling.
- There is no access-type metadata in this header. It does not tell consumers whether a field is read-only, write-only, write-one-to-clear, sticky, self-clearing, privileged, or firmware-owned.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include GC 11.5.0 support. Missing, renamed, or malformed macros should surface as compile failures in `gfxhub_v11_5_0.c` or code that adopts this generated header.
- Mechanically compare every `__SHIFT` and `_MASK` in this chunk against AMD's authoritative GC 11.5.0 register database.
- Cross-check that every register group in this chunk has a matching offset entry in `gc_11_5_0_offset.h`.
- Run mask/shift consistency checks: masks should align with shifts, full-width fields should be `0xFFFFFFFFL`, high address fields should use the expected reduced width, and repeated ME/HQD/watchpoint/GDS families should differ only where the hardware definition says so.
- Boot affected hardware and validate gfxhub initialization, especially the `CP_DEBUG` halt-disable bit used by `gfxhub_v11_5_0.c`, VM fault handling, TLB invalidation, and reset paths.
- Exercise compute and graphics queue creation/destruction, MES/HQD programming, packet queue doorbells, read/write pointer polling and writeback, EOP handling, IB execution, dequeue/preemption/suspend/resume, and queue reset/relaunch.
- Exercise KFD debugger paths that program `SPI_GDBG_PER_VMID_CNTL`, including trap enable, exception masks, trap-on-start/end, and wave launch mode.
- Exercise TCP and CP DMA watchpoints with aligned and boundary addresses, VMID-specific and any-VMID modes, read/write watches, and status reporting.
- Exercise GDS/GWS/OA allocation and release across multiple VMIDs, VMID reuse, GPU reset, and process teardown.
- Check runtime diagnostics: DRM/KFD logs, CP/CPC/ME pipe interrupt status, `CP_HQD_ERROR`, UTCL1 fault/retry/PRT status, ECC/EDC first occurrence fields, DDID counters, HQD dequeue/status fields, and GDS resource state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002554`. The final per-file research should merge this with neighboring chunks for full `gc_11_5_0_sh_mask.h` coverage. The previous chunk contains the start of `CP_ECC_FIRSTOCCURRENCE`; the next chunk completes `GDS_OA_VMID3` and continues the remaining GDS OA and reset/resource definitions.

### subset-b-002555: lines 14859-17371

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 14859-17371

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains C preprocessor constants only: each register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the GDS ordered-append VMID mask family, covering `GDS_OA_VMID4` through `GDS_OA_VMID15`, then describe GDS/GWS resource resets, GDS context-switch status/counters, and GDS memory-clean control. The middle of the chunk switches to `addressBlock: gc_rasdec` for RAS signature-control and signature registers. The rest is the beginning of `addressBlock: gc_gfxdec0`, covering depth-buffer, scan converter, color-buffer, viewport, clip-plane, variable-rate-shading, command-processor context identity, and pixel-shader input-control state. The range ends after the `SPI_PS_INPUT_CNTL_29__USE_DEFAULT_ATTR1_MASK` macro; the remaining masks for `SPI_PS_INPUT_CNTL_29` continue in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 11.5.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_11_5_0_sh_mask.h` supplies bit layouts for GC 11.5.0 registers. AMDGPU code combines these masks with register addresses from the matching `gc_11_5_0_offset.h` header and usually accesses fields through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`. This lets engine setup, command submission, debug, reset, and state-restore code program one hardware field without embedding raw bit positions.

This chunk focuses on graphics context and render-state metadata:

- GDS and GWS controls for per-VMID ordered-append masks, per-resource reset bits, single-resource reset by ID, OA reset masks by ME/pipe, context-switch read/write status, context-switch up/down pointer counters for CS/PS/GS paths, packer-index selection, and memory clean start/finish bits.
- RAS decode registers for enabling signature collection, masking the input bus, and exposing full-width signatures for SX, DB, PA, SC, SPI, CB, and BCI blocks.
- DB state for depth/stencil render control, z-pass counting, depth view dimensions and slices, depth/stencil compression and override behavior, HTILE and depth/stencil base addresses, depth bounds, clear values, Z/stencil surface formats, cache policy, and VRS center offsets.
- PA/SC state for screen/window/generic/viewport scissors, clip-rectangle rules, edge rules, hardware screen offsets, 16 viewport scissor rectangles, 16 viewport Z min/max pairs, raster configuration, screen extent, tile steering, and VRS surface/feedback base, size, override, and cache policy.
- CB state for target and shader masks, GL2 cache policy, blend constants, FDCC controls, coverage export, and color/depth/stencil interaction.
- PA/CL state for 16 viewport transform groups (`XSCALE`, `XOFFSET`, `YSCALE`, `YOFFSET`, `ZSCALE`, `ZOFFSET`) and six user clip planes with X/Y/Z/W components.
- SPI pixel-shader input controls `SPI_PS_INPUT_CNTL_0` through the partial `SPI_PS_INPUT_CNTL_29`, describing attribute offsets, default values, flat shading, primitive attributes, duplicate handling, FP16 interpolation, secondary-default behavior, and attribute validity.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the 32-bit register value.
- Register-address symbols live in the companion offset header, commonly as `mm...` symbols matching the same register name.
- AMDGPU callers normally combine these with register helpers, MMIO accessors, PM4 packet construction, context-save/restore tables, debug dumps, and register validation paths.

The main macro families in this chunk are:

- `GDS_OA_VMID4..15`: ordered-append VMID mask registers. Each has a 16-bit `MASK` field and high `UNUSED` bits.
- `GDS_GWS_RESET0`, `GDS_GWS_RESET1`, and `GDS_GWS_RESOURCE_RESET`: 64 bit-addressable GWS resource reset bits plus an indexed reset form with `RESET` and `RESOURCE_ID`.
- `GDS_OA_RESET_MASK` and `GDS_OA_RESET`: reset enables for ME0 graphics/compute and ME1/ME2 pipe reset targets, plus an indexed pipe-reset form.
- `GDS_*_CTXSW_STATUS`, `GDS_*_CTXSW_CNT*`, and `GDS_PS_CTXSW_IDX`: context-switch status bits (`R`, `W`), 16-bit `UPDN`/`PTR` counter packing, and a PS packer selector.
- `RAS_SIGNATURE_*` and `RAS_*_SIGNATURE*`: RAS signature enable/mask and full 32-bit signature readouts for shader export, depth buffer, primitive assembly, scan converter, SPI, color buffer, and BCI units.
- `DB_*`: depth/stencil render controls, count controls, view/surface info, address low/high pairs, compression/decompression overrides, clear values, stencil operations, and RMI/L2 cache controls.
- `PA_SC_*`: scissor, clip rectangle, viewport Z range, raster mapping, screen extent, tile steering, VRS override/base/size/cache, and VRS feedback surface fields.
- `CB_*`: color target write masks, shader-output masks, GL2 cache policy, blend constants, FDCC, coverage export, and related color-buffer control fields.
- `PA_CL_VPORT_*` and `PA_CL_UCP_*`: full-width floating-point viewport transforms and user clip-plane coefficients.
- `SPI_PS_INPUT_CNTL_*`: repeated per-attribute pixel-shader input controls. Entries 0-18 include `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `ROTATE_PC_PTR`, `PRIM_ATTR`, `PT_SPRITE_TEX`, `OUT_OF_ORDER_RT`, `DUP`, `FP16_INTERP_MODE`, `USE_DEFAULT_ATTR1`, `DEFAULT_VAL_ATTR1`, `ATTR0_VALID`, and `ATTR1_VALID`. Entries 19-29 use the same layout minus the point-sprite and out-of-order RT fields in this generated slice.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied AMDGPU runtime flow is:

1. Select the GC 11.5.0 register headers for the active ASIC.
2. Select the matching register address from `gc_11_5_0_offset.h`.
3. Read an existing register, prepare a context-state value, build a PM4 packet, or decode a debug/status dump.
4. Use the `__SHIFT` and `__MASK` pair, commonly through register field helpers, to pack or extract the relevant field.
5. Pass the composed value to graphics context setup, render-target/depth-state programming, viewport/scissor setup, VRS setup, shader-input routing, RAS signature checking, GDS/GWS reset, or hang/debug paths.

For render state, driver or userspace-generated command streams program DB, CB, PA/SC, PA/CL, and SPI context registers as part of graphics pipeline state. For GDS and RAS, flows are more diagnostic or maintenance oriented: reset selected GWS/OA resources, poll context-switch state, trigger memory clean, or collect block signatures. The header does not define ordering, synchronization, readback latching, or side-effect semantics; those are encoded in AMDGPU code, firmware interfaces, and the hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

GDS/GWS fields represent live global-data-share and global-wave-sync state. Resource reset fields have side effects, OA VMID masks govern which VMIDs can participate in ordered append behavior, and context-switch counters/status bits expose state that can change while engines are active. `GDS_MEMORY_CLEAN` start/finish fields imply a stateful hardware operation and should be treated as volatile rather than static configuration.

RAS signature fields are diagnostic state. `RAS_SIGNATURE_CONTROL__ENABLE` changes whether signatures are captured, `RAS_SIGNATURE_MASK` controls input masking, and the signature registers expose block-dependent values that may be valid only under the expected capture window. These values may be latched or stale according to hardware sequencing outside this header.

DB, CB, PA/SC, PA/CL, and SPI registers are graphics context state. They are programmed by command streams and can be saved/restored across context switches, suspend/resume, reset recovery, or virtualization boundaries. Depth/stencil base addresses and VRS surface bases are split low/high 256-byte address fields; viewport transforms and clip planes are full 32-bit data fields that usually encode floating-point values; scissor and rectangle fields pack signed or unsigned coordinate-like values into low/high halves.

Cache-policy, compression, HTILE, DCC/FDCC, partial-residency, fault-behavior, and no-allocate fields can affect memory traffic, correctness, and performance. Reserved and `UNUSED` fields appear throughout the generated map and should generally be preserved during read-modify-write unless the hardware sequence requires a documented full-register write.

SPI PS input controls define shader linkage state. Incorrect `OFFSET`, default-value, flat-shade, primitive-attribute, FP16 interpolation, duplicate, or attribute-valid bits can cause pixel shaders to read the wrong interpolants, substitute unexpected defaults, or mis-handle primitive/attribute data. The repeated layout means a one-bit drift can affect a single attribute lane while the rest of the pipeline appears healthy.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_default.h`, if present in the same register family, provides default/reset values for many registers.
- AMDGPU common register helper macros provide field packing/extraction and MMIO or command-packet access mechanisms.
- AMDGPU graphics, GDS, CP context, RAS, reset, debug, hang-dump, KFD/compute-adjacent, and power-management paths can include these generated constants.
- Userspace graphics stacks indirectly depend on these fields through kernel command submission, context register validation, and ASIC-specific packet/register programming expectations.

Integration points include GWS resource reset and cleanup, ordered-append behavior, GDS context-switch diagnostics, RAS signature collection, depth/stencil target setup, HTILE and Z/stencil base programming, color target write masks, DCC/FDCC behavior, GL2/RMI cache policy, VRS rate and feedback surface setup, rasterizer/scissor/viewport state emission, user clip-plane programming, command-processor context identity registers (`CP_PIPEID`, `CP_RINGID`, `CP_VMID`), performance-monitor context enablement, primitive restart index state, and pixel-shader interpolant setup.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bits or decode misleading state.
- This chunk starts and ends mid-family. It begins after the first GDS OA VMID entries and ends before the last masks for `SPI_PS_INPUT_CNTL_29`; adjacent chunk research is needed for complete file-level conclusions.
- Repeated register families are easy to validate superficially but still risk single-index errors: GDS VMID masks, viewport scissors, viewport transforms, clip planes, and SPI input controls all repeat similar layouts.
- Reset fields such as `GDS_GWS_RESET*`, `GDS_GWS_RESOURCE_RESET`, and `GDS_OA_RESET*` have hardware side effects. Treating them like passive status fields can lose active synchronization resources or disrupt queues.
- Split address fields such as DB Z/stencil/HTILE bases and VRS base/feedback bases are 256-byte based with separate high registers. Incorrect alignment or high-word composition can point hardware at the wrong memory.
- DB compression, decompression, HTILE, DCC/FDCC, fault-behavior, partial-residency, and cache-policy fields affect correctness under render compression, sparse residency, reset recovery, and memory-fault conditions.
- Scissor, viewport, clip rectangle, and raster configuration masks determine screen-space clipping and shader export behavior. Incorrect sign/width assumptions can produce subtle rendering corruption rather than hard failures.
- RAS signatures are only useful when capture enable, input mask, block activity, and read timing match the hardware diagnostic sequence. This header cannot express those timing requirements.
- `UNUSED`, `RESERVED_FIELD_*`, and `DB_RESERVED_REG_*` macros expose bit positions but do not make those bits safe to program arbitrarily.
- `SPI_PS_INPUT_CNTL_*` fields are shader ABI sensitive. Attribute routing errors can manifest as wrong interpolation, incorrect primitive attributes, broken flat shading, or rendering failures isolated to particular pixel-shader inputs.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware/runtime graphics diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_11_5_0_sh_mask.h`, especially GC 11.5.0 graphics, GDS, RAS, reset, debug, and context-state paths.
- Mechanical comparison against AMD's authoritative GC 11.5.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 14859-17371.
- Cross-checks that registers in this chunk have matching address macros in `gc_11_5_0_offset.h` and expected defaults in the matching default header where generated.
- Static sanity checks that masks align with shifts, full-width data fields use `0xFFFFFFFFL`, split address high/low widths match the register specification, and repeated families remain structurally consistent across indices.
- Render tests covering depth/stencil clear/copy/decompress, HTILE, depth bounds, stencil front/back operations, color target masks, shader output masks, blend constants, and coverage export.
- Viewport and rasterization tests covering all 16 viewports, screen/window/generic/viewport scissors, clip rectangles, user clip planes, primitive restart, edge rules, raster configuration, and tile steering.
- VRS tests covering override modes, rate surfaces, feedback surfaces, cache-policy fields, base/high address composition, and size fields.
- Pixel-shader interpolation tests that exercise flat shading, default attribute values, primitive attributes, duplicate inputs, FP16 interpolation, point-sprite coordinates, and attribute-valid bits across the `SPI_PS_INPUT_CNTL_*` range.
- GDS/GWS tests or debug traces that reset selected resources, validate OA VMID masks, observe context-switch counters, and confirm memory-clean start/finish behavior.
- RAS or diagnostic tests that enable signature capture, apply input masks, and compare SX/DB/PA/SC/SPI/CB/BCI signatures under controlled workloads.
- Runtime warning signals include rendering corruption, wrong depth/stencil behavior, broken VRS feedback/rate images, incorrect shader interpolants, GDS resource reset side effects, bad RAS signatures, GPU hangs during context restore, or debug dumps with impossible context/viewport/scissor state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002555`. It covers lines 14859-17371 of `gc_11_5_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the earlier `GDS_OA_VMID*` family and the trailing `SPI_PS_INPUT_CNTL_29` masks, and to place these GDS/RAS/GFXDEC0 definitions in the full GC 11.5.0 register map.

### subset-b-002556: lines 17372-19737

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 17372-19737

## Purpose

This chunk is generated AMD GC 11.5.0 shader/register field metadata. It contains no executable C logic; it publishes preprocessor constants for register-field bit positions and masks in the graphics command/raster/DB/CB pipeline. Consumers combine these `REG__FIELD__SHIFT` and `REG__FIELD_MASK` macros with register offsets from the matching GC 11.5.0 offset header and register access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and related AMDGPU macros.

The requested range is a mid-file slice of `gc_11_5_0_sh_mask.h`. It starts at the tail of `SPI_PS_INPUT_CNTL_29`, covers complete shader interpolator, vertex geometry/tessellation, primitive assembly, rasterizer, scan converter, depth buffer, blending, and color-buffer render-target field definitions, and stops after the beginning of the `CB_COLOR7_VIEW` field set. The chunk contains 184 register comment groups and 2,182 `#define` lines: 1,090 `__SHIFT` macros and 1,092 `_MASK` macros.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, allocation paths, or locks in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the zero-based bit position used to insert or extract a field value.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field after it is shifted into register position.

These macros are consumed by token-pasting helpers. For example, `REG_SET_FIELD(value, VGT_SHADER_STAGES_EN, VS_W32_EN, 1)` expands through `VGT_SHADER_STAGES_EN__VS_W32_EN__SHIFT` and `VGT_SHADER_STAGES_EN__VS_W32_EN_MASK`. The related CGS helpers in `include/cgs_common.h` use the same naming contract through `CGS_REG_FIELD_SHIFT`, `CGS_REG_FIELD_MASK`, `CGS_REG_SET_FIELD`, and `CGS_REG_GET_FIELD`.

Major macro families in this slice:

- `SPI_*`: pixel-shader input controls for parameters 30 and 31, vertex-shader export counts, pixel-shader input enable/address bits, interpolation controls, barycentric controls, temporary ring size, scratch base address, and shader export format fields.
- `SX_*` and `CB_BLEND*_CONTROL`: shader export down-conversion, blend optimization epsilon/control fields, per-MRT source/destination blend optimization, and per-render-target color/alpha blend factors/functions/enables.
- `DB_*`: depth/stencil test control, EQAA sample-count and quality fields, shader depth/export behavior, HTILE surface metadata, stencil-results compare state, preload windows, alpha-to-mask, and depth bias format support.
- `PA_CL_*`, `PA_SU_*`, and `PA_SC_*`: clipping, viewport transform, vertex output semantics, NaN/Inf handling, culling, polygon mode/offset, point and line sizes, primitive filtering, stereo and VRS controls, scan-converter mode, anti-alias sample locations and masks, conservative rasterization, NGG mode, shader-control, and primitive binning fields.
- `VGT_*`, `GE_*`, `IA_*`, and `WD_*`: draw initiation, DMA/index-buffer state, primitive ID, event initiation, draw payload, ESGS ring item size, tessellation distribution, shader-stage enablement, LS/HS and tessellation factor parameters, streamout draw state, GS output limits, and NGG subgroup sizing.
- `CB_COLOR0` through `CB_COLOR6` plus the start of `CB_COLOR7`: render-target base, view, format/number type/component swap/blend optimization, fragment attributes, FDCC/DCC compression controls, and DCC base-address fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing belongs to the graphics driver, firmware, command processor packets, and user-mode graphics stack that program the registers represented here:

1. AMDGPU code includes `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h` for GC 11.5.0 ASIC support.
2. Code forms register values by shifting and masking individual fields, usually through `REG_SET_FIELD` or `REG_GET_FIELD`.
3. Register offsets are supplied by the offset header and passed to direct MMIO helpers such as `RREG32_SOC15`/`WREG32_SOC15`, indirect accessors, or command-buffer packet emission paths.
4. Hardware consumes the resulting state during draw dispatch, tessellation, geometry/NGG processing, rasterization, depth/stencil testing, blending, compression, and render-target writes.

Within this repository snapshot, the exact `gc_11_5_0_sh_mask.h` include is visible in `amdgpu/gfxhub_v11_5_0.c`, where other fields from the same generated header are used for VM/GFXHUB programming and fault decode. Direct C references to the specific 3D pipeline masks in this chunk were not found in the searched AMDGPU/display/PM sources, which is expected for generated register databases: some fields are used by packet builders, shared macro tables, out-of-tree consumers, or retained for ASIC completeness even when not referenced by this kernel slice.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed and command-processor-visible GPU state. The represented state includes:

- Pixel-shader interpolation and barycentric state: which inputs are enabled, where they are addressed, flat-shade behavior, default attributes, FP16 interpolation, and primitive-attribute routing.
- Shader export and blend state: render-target format mapping, down-conversion, blend optimization, per-MRT blend controls, color-control modes, and ROP behavior.
- Depth and stencil state: Z/stencil enablement, comparison functions, write enables, bounds testing, EQAA/coverage behavior, shader Z/stencil/mask export controls, HTILE-related surface fields, preload regions, and alpha-to-mask.
- Rasterization state: clipping/culling rules, viewport transform enablement, point/line/raster mode controls, sample positions and sample masks, centroid priority, primitive filtering, VRS, conservative rasterization, and binning/NGG behavior.
- Vertex geometry/tessellation state: draw source, index-buffer address/type, shader-stage enables, LS/HS and tessellation factor parameters, primitive ID, streamout opaque-draw registers, and GS/NGG subgroup limits.
- Render-target state: color buffer base addresses, array slice/mip views, format/number type/component swap fields, fragment count attributes, DCC/FDCC compression toggles, and DCC base addresses for color slots 0 through 6 in this chunk.

Persistence is hardware-defined. Most context registers retain programmed values until the next context restore, command stream update, modeset-like graphics reset, GPU reset, suspend/resume, or power-gating transition. Status/debug/counter fields, event initiators, and clear/copy/decompress controls may be transient, sticky, write-one-to-clear, or sequencing-sensitive, but this generated mask header does not encode access type or side-effect semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated GC 11.5.0 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` for the corresponding `reg...` or `mm...` register offsets.
- Other GC 11.5.0 generated headers, including any default-value and enum headers used by the same ASIC support code.
- AMDGPU register helpers that assume the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming contract, including `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15*`, `CGS_REG_SET_FIELD`, and `CGS_REG_GET_FIELD`.

Observed direct include site:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`

Broader integration points are the GC graphics pipeline and command submission paths. Render state represented by this chunk is normally derived from API pipeline state, shader metadata, framebuffer attachments, MSAA/VRS/depth-stencil configuration, and tiling/compression layout decisions, then emitted as register writes or command packets. The `CB_COLOR*`, `DB_*`, `PA_*`, `SPI_*`, `SX_*`, and `VGT_*` families line up with classic GPU pipeline stages: shader input/export, primitive assembly, tessellation/geometry, clipping/setup, rasterization, depth/stencil, blending, and color output.

## Risks And Edge Cases

- Field drift is the central risk. These macros are untyped constants, so an incorrect shift or mask can compile cleanly while corrupting unrelated bits in a hardware register.
- Generated-header pairing matters. A GC 11.5.0 mask header used with the wrong offset/default/enum header can address the right-looking symbolic register name with incompatible bit layout.
- Repeated render-target and MRT families are copy-sensitive. `CB_BLEND0` through `CB_BLEND7` and `CB_COLOR0` through `CB_COLOR6` are structurally similar but slot-specific; one bad generated value may only fail with multiple render targets, a high-numbered color attachment, or DCC/FDCC enabled.
- Chunk boundaries are artificial. The first line is the tail of `SPI_PS_INPUT_CNTL_29`, while the end stops inside the `CB_COLOR7` register family. Adjacent chunks are required before making complete claims about all pixel-shader input controls or all eight color-buffer slots.
- Compression and render-target fields are high impact. Incorrect `CB_COLOR*_FDCC_CONTROL`, `CB_COLOR*_DCC_BASE`, or format/number-type masks can cause visual corruption, incorrect blending, GPU faults, or data loss in compressed render targets.
- Rasterization fields interact with subtle API behavior. Incorrect sample locations, sample masks, conservative rasterization, VRS, centroid priority, flat shading, clip/cull, or viewport-transform fields can produce failures limited to MSAA, VRS, tessellation, geometry-shader, point/line, or conservative-raster workloads.
- Depth/stencil state is side-effect-sensitive. Misprogrammed DB fields can break early/late Z, stencil export, alpha-to-coverage, HTILE use, depth clears/copies/decompresses, or shader depth export ordering.
- Several fields are architectural or reserved-looking in this generated view. Consumers must rely on ASIC documentation and existing driver sequencing, not infer writability or reset values from the presence of a mask.

## Test Signals

Useful validation is a mix of generated-header consistency, build coverage, and graphics behavior:

- Build AMDGPU with GC 11.5.0 support enabled; missing or renamed macros should fail in code that includes `gc_11_5_0_sh_mask.h` and uses `REG_SET_FIELD`/`REG_GET_FIELD`.
- Mechanically verify that field masks are compatible with shifts for each register and that repeated families such as `CB_BLEND*`, `SX_MRT*_BLEND_OPT`, `PA_SC_AA_SAMPLE_LOCS_*`, and `CB_COLOR*` retain expected slot-to-slot structure.
- Diff this generated chunk against AMD's authoritative GC 11.5.0 register database and against nearby GC 11.x headers where compatibility is expected; intentional ASIC deltas such as new `PRIM_ATTR`, `NUM_PRIM_INTERP`, W32, NGG, VRS, FDCC, and binning fields should be reviewed explicitly.
- Run graphics conformance and stress workloads that cover the represented pipeline state: multi-render-target blending, integer/float render-target formats, alpha-to-coverage, MSAA sample positions/masks, depth/stencil tests and shader depth export, conservative rasterization, VRS, primitive filtering, tessellation, geometry/NGG, streamout opaque draws, and indexed draws.
- Exercise DCC/FDCC paths with color compression enabled and disabled, including clears, resolves, copies, decompression, render-target transitions, and high-numbered color slots.
- Watch kernel logs, GPU fault reports, hangs, visual corruption, CRC mismatches, render-target compare failures, and reset/recovery paths. GFXHUB VM faults from CB/DB clients are especially relevant because incorrect render-target or depth state can surface as memory access faults.

## Cross-Chunk Notes

The previous chunk owns the earlier `SPI_PS_INPUT_CNTL_*` definitions and the beginning of this chunk starts with only the final mask lines for `SPI_PS_INPUT_CNTL_29`. Later chunks continue after `CB_COLOR7_VIEW` and are needed for complete coverage of color slot 7 and the rest of the GC 11.5.0 shader/register mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all render-target, depth-buffer, shader, or rasterization registers in `gc_11_5_0_sh_mask.h`.

### subset-b-002557: lines 19738-22220

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 19738-22220

## Purpose

This chunk is a middle slice of AMD's generated GC 11.5.0 shift/mask register-field header. It has no executable C logic; it exports preprocessor constants that describe bit positions and bit masks for graphics-core MMIO register fields. Driver code pairs these macros with the matching GC 11.5.0 register offset header and AMDGPU register helper macros to pack, unpack, and update individual fields in hardware registers.

The requested range contains 2,160 `#define` entries: 1,081 `__SHIFT` macros and 1,079 `_MASK` macros. The chunk boundary starts inside `CB_COLOR7_VIEW` and ends inside `SPI_RESOURCE_RESERVE_CU_2`, so a few field pairs are intentionally split with adjacent chunks. The content spans the tail of color-buffer render-target metadata, then several GC address blocks covering command processor controls, GRBM, PA/SC rasterizer and binning controls, shader/SQ state, CP queue debug state, DIDT/EDC throttling, SPI/TCP/GDS/UTCL1/GCR controls, CAC/EDC power accounting, and the beginning of SPI per-CU resource reservation fields.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: mask used to isolate or preserve a field.

The main register families in this range are:

- `CB_COLOR*`: color-buffer target fields for `CB_COLOR7_VIEW`, `CB_COLOR7_INFO`, `CB_COLOR7_ATTRIB`, `CB_COLOR7_FDCC_CONTROL`, DCC base extension fields for targets 0-7, and `ATTRIB2`/`ATTRIB3` geometry and swizzle metadata for color targets 0-7.
- `CP_MEC_CNTL`, `CP_ME_CNTL`, `CP_FETCHER_SOURCE`, and `CP_HPD_*`: command processor micro-engine controls, halt/reset and clock-gating controls, high-priority dispatch ROQ offsets, and HPD queue status/force/freeze fields.
- `GRBM_GFX_CNTL` and `GRBM_NOWHERE`: graphics register bus manager instance selection and nowhere-routing fields used by low-level register access paths.
- `PA_SC_*` and `PA_PH_*`: primitive assembly, scan converter, variable-rate shading, primitive binning, FIFO sizing, event controls, perf counters, screen trap locks, and out-of-order/PBB enhancement knobs.
- `SQ_*` and `SH_MEM_*`: shader runtime/debug status, shader memory bases/configuration, trap base address and memory address fields.
- `DIDT_*`, `GC_EDC_*`, `GC_THROTTLE_*`, `PCC_*`, and `PWRBRK_*`: dynamic inductive/droop thermal controls, energy droop control thresholds, stall patterns, hysteresis, throttle sources, status, overflow, rolling power delta, and performance counters.
- `SPI_*`, `PC_CONFIG_*`, and `SPI_COMPUTE_WF_CTX_SAVE_STATUS`: shader processor interface debug stalls/traps, arbitration and resource limits, primitive control configuration, compute wavefront context-save busy bits across pipes and queues, and per-CU resource reservation fields.
- `TCP_*`, `GDS_*`, `UTCL1_*`, `GCR*`: texture cache invalidation/status/cntl fields, GDS clock-gating restore controls, UTCL1 control and FIFO sizing, GCR target disable, cache/TLB command status, credits, and spare fields.
- `GC_CAC_*`, `SE_CAC_*`, and numerous `*_CAC_WEIGHT_*` registers: global and shader-engine CAC windows, aggregate counters, indirect index/data accessors, and subsystem-specific weighting fields for CP, EA, UTCL2, GDS, GL2C, SDMA, SQ, TCP, CB, DB, PA, SC, SPI, and related blocks.

Several names include `MASK` as part of the hardware field name, such as `GC_EDC_CTRL__THROTTLE_SRC0_MASK__SHIFT` paired with `GC_EDC_CTRL__THROTTLE_SRC0_MASK_MASK`. Consumers must treat the full macro spelling as generated ABI rather than applying ad hoc suffix parsing.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU code that includes this generated header:

1. GC 11.5.0 initialization code selects register offset, shift, and mask tables for the ASIC.
2. Register-list macros token-paste symbolic register and field names into helper calls or table initializers.
3. Runtime paths use AMDGPU helpers to read, write, or update MMIO registers while applying these masks and shifts.
4. Hardware blocks then interpret the programmed values for render-target setup, rasterization/binning behavior, queue management, shader debugging, cache/TLB invalidation, throttling, and power/accounting controls.

The macros do not encode sequencing, access permissions, side effects, reset values, or read/write legality. Consumers still need hardware-specific ordering around CP queue changes, GRBM instance selection, cache invalidation, CAC/EDC/throttle programming, shader trap setup, suspend/resume restore, and reset recovery.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes hardware state held in GC 11.5.0 registers:

- Color-buffer state for target format, view, DCC/FDCC compression, base extension, dimensions, swizzle mode, resource type, and DCC pipe alignment.
- PA/SC state for variable-rate shading feedback, PBB/binning, out-of-order scan conversion, FIFO sizing, wave ID tables, event masks, and perf counters.
- SQ/SPI/PC state for debug stalls, trap enablement, shader memory base/configuration, resource limits, wave context-save status, and primitive/attribute flow control.
- CP and HPD queue state for micro-engine control, queue availability, fetch/MQD activity, pending transfer size, force/freeze controls, and ROQ offsets.
- Cache and translation state for TCP invalidation, UTCL1 controls, GCR target disable/status, TLB shootdown, request credits, and error status.
- Power and reliability state for DIDT, EDC, PCC, PWRBRK, CAC windows, aggregate counters, weight registers, throttle status, overflow counters, and stretch/performance counters.

Persistence is defined by the hardware block and power domain. Many configuration fields persist until modeset, engine reinitialization, power-gating, suspend/resume, GPU reset, or ASIC reset. Status and counter fields may be read-only, sticky, write-one-to-clear, self-clearing, saturating, indirect-indexed, or only valid while related clocks are active. This header does not mark those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated GC 11.5.0 register database and must stay synchronized with the companion offset and default-value headers for the same ASIC family, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which provides matching register offsets.
- Other generated `gc_11_5_0_*` headers that describe default values or field values where present.
- AMDGPU GC, CP, RLC, MEC, KFD, power-management, reset, debug, and performance-monitoring code that builds register tables or direct register helper calls from these macro names.
- Firmware and microcode interfaces for CP/MEC/HPD queues, DIDT/EDC throttling, CAC accounting, and cache/TLB control, where driver-visible register programming must match firmware expectations.

The most behaviorally sensitive integration points are render-target programming (`CB_COLOR*`), rasterizer/binning configuration (`PA_SC_*`), queue/debug controls (`CP_*`, `SQ_*`, `SPI_*`), cache/TLB invalidation and target disable (`TCP_*`, `UTCL1_*`, `GCR*`), and thermal/power throttling (`DIDT_*`, `GC_EDC_*`, `GC_CAC_*`, `SE_CAC_*`).

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile successfully while programming the wrong MMIO bits.
- Manual edits are high risk because this generated file must match AMD's authoritative register database, the offset header, firmware assumptions, and silicon behavior.
- The chunk has artificial boundaries. `CB_COLOR7_VIEW__SLICE_START__SHIFT` is before this range while its mask is inside it, and `SPI_RESOURCE_RESERVE_CU_2` continues after line 22220.
- Some generated field names contain `MASK` before the suffix. Tools that strip `_MASK` or `__SHIFT` naively can report false mismatches or generate wrong field names for `GC_EDC_CTRL__THROTTLE_SRC*_MASK`.
- Repeated register families invite single-instance generator errors. `CB_COLOR0-7`, `PA_SC_BINNER_EVENT_CNTL_0-3`, CAC weight families, and `SPI_RESOURCE_RESERVE_CU_*` should be checked per instance, not assumed correct from one representative.
- Side-effect-sensitive status/control fields can cause hangs, interrupt storms, bad queue state, or broken reset recovery if consumers confuse read-only status, write-one-to-clear status, force/freeze controls, or clock-gating overrides.
- Power/throttle fields can affect stability and performance. Incorrect DIDT, EDC, PCC, PWRBRK, CAC, or stall-pattern fields may over-throttle, under-throttle, misreport counters, or break firmware-mediated power management.
- Cache/TLB and target-disable fields are correctness-sensitive. Wrong `GCR_CMD_STATUS`, UTCL1, TCP invalidation, or target disable masks can leave stale translations/cache lines or incorrectly disable shader-engine/GL2 targets.

## Test Signals

Useful validation signals include:

- Build AMDGPU with GC 11.5.0 support enabled. Missing or renamed macros should fail where GC 11.5 register tables and helper calls reference these fields.
- Mechanically compare this range against the authoritative AMD generated register database and the matching `gc_11_5_0_offset.h` register names.
- Run a shift/mask pairing check that understands fields whose generated names already contain `MASK`, and allow the expected chunk-boundary splits at `CB_COLOR7_VIEW` and `SPI_RESOURCE_RESERVE_CU_2`.
- Exercise graphics workloads that stress MRT color targets, DCC/FDCC compression, mips/array slices, MSAA fragments, PBB/binning, VRS, primitive discard/null primitive paths, and out-of-order scan conversion.
- Exercise compute and queue paths through KFD/AMDGPU: queue create/destroy, preemption, context save/restore, CP/MEC reset, MQD fetch, and debug halt/freeze paths.
- Validate cache/TLB behavior under VM faults, eviction, TLB shootdowns, GPU reset, suspend/resume, and heavy memory pressure.
- Monitor power-management and telemetry behavior for DIDT/EDC/PCC/PWRBRK/CAC counters, throttle status, overflow counters, and performance regressions under thermal or power-limit stress.
- Watch kernel logs, GPU reset traces, debugfs/sysfs telemetry, perf counters, and hang reports for invalid register programming, stuck busy bits, queue state mismatches, cache invalidation failures, or unexpected throttling.

## Cross-Chunk Notes

This is not the whole `gc_11_5_0_sh_mask.h` file. Earlier chunks contain the header guard, many preceding GC register families, and the first part of `CB_COLOR7_VIEW`. Later chunks continue `SPI_RESOURCE_RESERVE_CU_2` and the rest of the GC 11.5.0 generated shift/mask namespace. The final per-file research document should synthesize all chunks before making whole-file claims about complete register coverage or all GC 11.5.0 integration points.

### subset-b-002558: lines 22221-24948

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 22221-24948

## Purpose

This chunk is part of AMDGPU's generated GC 11.5.0 register field header. It contains C preprocessor constants for register field shifts and masks, not executable code. Driver code combines these `*_SHIFT` and `*_MASK` definitions with the matching register offsets from `gc_11_5_0_offset.h` and helper macros such as `REG_SET_FIELD()` / `REG_GET_FIELD()` in `amdgpu.h` to read, modify, and decode memory-mapped GPU registers.

The span starts in the `gc_pfonly2_spidec` address block with SPI compute-unit reservation fields, covers the large `gc_gfxudec` graphics/user-data command processor and graphics frontend register block, and enters the `gc_cprs64dec` block for RS64/MES/MEC command processor microcontroller state. The chunk ends mid-register at `CP_GFX_RS64_GP0_HI0__M_RET_ADDR__SHIFT`; the following chunk must complete that register's mask and the remaining RS64 GP register definitions.

## Important APIs, Types, And Macro Families

This file defines no functions, structs, or runtime types. Its public interface is macro names of the form:

- `REGISTER__FIELD__SHIFT`: bit offset for `FIELD` inside `REGISTER`.
- `REGISTER__FIELD_MASK`: bitmask for the same field.

The consumer API is outside this file:

- `REG_SET_FIELD(orig_val, reg, field, field_val)` token-pastes `reg##__##field##__SHIFT` and `reg##__##field##_MASK` to insert a field value.
- `REG_GET_FIELD(value, reg, field)` uses the same generated symbols to extract a field.
- `RREG32_SOC15`, `WREG32_SOC15`, and related SOC15 helpers perform the actual MMIO register access using the corresponding `reg...` offset macros.

Major register groups in this chunk:

- `SPI_RESOURCE_RESERVE_CU_2` through `SPI_RESOURCE_RESERVE_CU_15` and `SPI_RESOURCE_RESERVE_EN_CU_0` through `SPI_RESOURCE_RESERVE_EN_CU_15`: per-CU resource reservation controls for VGPR, SGPR, LDS, wave, barrier, enable, type mask, and queue mask fields.
- `CP_EOP_*`, `CP_PIPE_STATS_*`, `CP_VGT_*`, `CP_PA_*`, `CP_SC_*`: command processor event/fence addresses and graphics pipeline statistics/counter registers.
- `SCRATCH_REG*`, `SCRATCH_REG_ATOMIC`, `SCRATCH_REG_CMPSWAP_ATOMIC`: generic CP scratch registers plus atomic/compare-swap fields.
- `CP_APPEND_*`, `CP_*ATOMIC*_PREOP_*`, `CP_ME_MC_*`, `CP_SEM_*`, `CP_WAIT_*`: append buffer, atomic pre-op, memory-controller read/write, semaphore, and wait-register-memory control fields.
- `CP_DMA_PFP_*`, `CP_DMA_ME_*`, `CP_DMA_CNTL`, `CP_DMA_READ_TAGS`: packet/control fields for CP DMA engines, including byte counts, source/destination selection, endian swap, engine and command fields, privilege, discard, and coherency flags.
- `CP_IB*`, `CP_ST_*`, `CP_DB_*`, `CP_DRAW_INDX_INDR_*`, `CP_DISPATCH_INDR_*`, `CP_INDEX_*`, `CP_GDS_BKUP_*`: indirect buffer, state buffer, draw/dispatch indirect, index, and GDS backup address/buffer-size definitions.
- `CP_EOP_DONE_EVENT_CNTL`, `CP_EOP_DONE_DATA_CNTL`, `CP_EOP_DONE_CNTX_ID`: end-of-pipe completion event/data generation controls.
- `CP_ME_COHER_*`: ME coherency control, base, size, and status fields.
- `RLC_GPM_PERF_COUNT_*`, `GRBM_GFX_INDEX`: performance counter and graphics-index selection fields.
- `VGT_*`, `GE_*`, `PA_*`: geometry engine, vertex grouper/tessellator, stereo, VRS, line stipple, screen extent, and trap-screen controls.
- `SQ_THREAD_TRACE_USERDATA_*`, `SQC_CACHES`, `TA_CS_BC_BASE_ADDR*`: shader trace userdata, shader cache controls, and texture/cache backing address fields.
- `DB_OCCLUSION_COUNT*`: depth-buffer occlusion counter fields.
- `GDS_*`: global data share read/write, atomics, global wave sync resources, ordered append controls, stream-out counters, and GS fields.
- `SPI_CONFIG_CNTL*`, `SPI_WAVE_LIMIT_CNTL`, `SPI_GS_THROTTLE_CNTL*`, `SPI_ATTRIBUTE_RING_*`: shader processor interpolator/global shader throttling, wave limits, context-save, power-save, and attribute ring configuration.
- `CP_MES_*`: MES RS64 firmware control, program counter, interrupt routing/status, RISC-V-like machine CSRs (`MSTATUS`, `MEPC`, `MCAUSE`, `MIP`, `MIE`, `MTIME`, etc.), icache/dcache controls, process quanta, doorbell controls, GP registers, local apertures, scratch base, perfcount, interrupt data, and sixteen data-cache apertures.
- `CP_MEC_*`: MEC RS64 firmware control, program counter, interrupt state, dcache controls, GP registers, local/instruction/scratch apertures, perfcount, interrupt data, and sixteen data-cache apertures.
- `CP_CPC_IC_OP_CNTL`, `CP_GFX_CNTL`, `CP_GFX_RS64_*`: command processor instruction-cache operation, graphics engine selection/config, RS64 interrupts, dcache control, local/instruction/scratch apertures, perfcount, timers, interrupt pending bits, and early GP register definitions.

## Control Flow

There is no local control flow. The effective flow is in consumers:

1. Read a 32-bit register with `RREG32_SOC15()` or prepare a zero value.
2. Insert fields with `REG_SET_FIELD()` using symbols from this header.
3. Write the value with `WREG32_SOC15()`.
4. Poll status bits with `REG_GET_FIELD()` when hardware exposes completion flags.

Examples elsewhere in the tree show the same contract: cache setup paths set `CP_CPC_IC_OP_CNTL.INVALIDATE_CACHE` and poll `INVALIDATE_CACHE_COMPLETE`; RS64 data-cache paths set `CP_GFX_RS64_DC_OP_CNTL.INVALIDATE_DCACHE` and poll `INVALIDATE_DCACHE_COMPLETE`; MES setup writes `CP_MES_CNTL` reset/active/halt fields, program-counter registers, scratch addresses, and optional `CP_MES_IC_OP_CNTL` invalidate/prime fields.

## State And Persistence Behavior

The macros themselves are compile-time constants and persist only as preprocessor definitions. The state they describe is hardware state:

- Many `CP_*`, `SPI_*`, `GE_*`, `VGT_*`, `GDS_*`, and `DB_*` registers persist in GPU MMIO/register files until reset, power-gating transitions, firmware reinitialization, or explicit driver writes.
- Address fields such as EOP, pipe stats, append, indirect buffer, data-cache aperture, local scratch, and firmware base registers point hardware blocks at GPU virtual/physical memory managed by AMDGPU.
- Counter/status registers, including pipeline stats, occlusion counters, GDS atomics, cache operation completion bits, and interrupt pending/data registers, are updated by hardware as command streams execute.
- Some fields are per-pipe/per-me/per-queue selected indirectly through GRBM/SRBM selection in consumer code; writes are only meaningful for the currently selected hardware instance.

## Dependencies

This chunk depends on the generated register offset namespace in `gc_11_5_0_offset.h`; mask macros alone do not name an MMIO address. It also depends on AMDGPU helper definitions in `amdgpu.h` for field composition/extraction and on SOC15 register access helpers for addressing GC instances.

The exact header is directly included by `amdgpu/gfxhub_v11_5_0.c` along with `gc_11_5_0_offset.h`. Other AMDGPU GFX/MES/MEC files use the same generated macro naming pattern for nearby ASIC versions and comparable register blocks, so the chunk participates in a broader generated-register ABI even when a specific function includes a sibling `gc_*_sh_mask.h`.

## Integration Points

- GFX hub/MMU code uses this header family to decode protection faults and program VM invalidation or address-translation registers.
- Command processor firmware loading/configuration uses `CP_CPC_IC_OP_CNTL`, `CP_GFX_RS64_DC_*`, `CP_MES_*`, and `CP_MEC_*` field definitions to point instruction/data caches at firmware buffers, invalidate or prime caches, control resets, and activate pipes.
- MES scheduling and KIQ setup use `CP_MES_CNTL`, `CP_MES_PRGRM_CNTR_START*`, `CP_MES_MSCRATCH_*`, `CP_MES_GP*`, doorbell controls, and interrupt fields to initialize and observe MES firmware execution.
- Graphics command submission and counters use `CP_IB*`, `CP_DRAW_INDX_INDR_*`, `CP_DISPATCH_INDR_*`, `CP_EOP_*`, `CP_PIPE_STATS_*`, `VGT_*`, `GE_*`, `DB_OCCLUSION_COUNT*`, and stream-out/GDS counter fields.
- Low-level debugging and fault analysis paths rely on the names staying aligned with hardware documentation because register dumps and decoded fields are interpreted by developers and diagnostic tooling.

## Risks

- A wrong shift or mask silently corrupts register programming. Because `REG_SET_FIELD()` token-pastes these names, build success does not prove that the bit layout matches hardware.
- Cross-generation similarity is a hazard. Registers such as CP/MES/MEC cache and aperture controls appear in GC 11/12 families but not always with identical fields. Copying masks between versions can program reserved or changed bits.
- This chunk ends in the middle of `CP_GFX_RS64_GP0_HI0`; any merge/reconciliation lane must combine adjacent chunks before treating the per-file research as complete.
- Repeated indexed register families (`*_CU_0..15`, `*_APERTURE0..15`, `*_INTERRUPT_DATA_16..31`) are prone to generator or review mistakes where one instance's mask differs accidentally from its siblings.
- Some fields describe security- or isolation-sensitive controls, including VMID, bypass mode, privilege, GDS resource limits, doorbells, scratch/aperture bases, and coherency/cache operations. Incorrect values can cause GPU hangs, memory corruption, cross-VM leakage, or failed firmware startup.
- The macros carry no runtime validation. Tests that only compile the driver may miss field-level regressions unless they exercise real register writes, firmware loading, or hardware polling paths.

## Test Signals

Useful signals for this chunk are mostly integration and hardware-facing:

- Build coverage for AMDGPU GC 11.5.0 paths, ensuring all generated macro names referenced by `REG_SET_FIELD()` and `REG_GET_FIELD()` resolve.
- Driver boot on GC 11.5.0 hardware with successful gfxhub initialization, firmware loading, MES enablement, and queue bring-up.
- No timeout logs from instruction/data cache operations, especially messages around failed CP/MES/MEC icache or RS64 dcache invalidation/priming.
- Successful graphics and compute command submission, indirect draw/dispatch, EOP fence signaling, doorbell handling, and context switching.
- Stable pipeline statistics, occlusion queries, stream-out counters, GDS atomics/global wave sync, and scratch/append-buffer operations under stress.
- Clean GPU reset/resume cycles, because many of these registers are reprogrammed after reset or power transitions.
- Register dump comparison against the GC 11.5.0 hardware specification or AMD-generated headers, especially for indexed aperture/resource families and cache-operation completion bits.

### subset-b-002559: lines 24949-27593

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 24949-27593

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains preprocessor constants only: each hardware register field has a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for packing and extracting 32-bit register values.

The requested range contains 1,054 `__SHIFT` constants and 1,054 `_MASK` constants. It begins in the middle of the `CP_GFX_RS64_GP0_HI0` register family, starting with the `M_RET_ADDR` mask whose shift was in the previous chunk, and ends on a complete `SPI_PERFCOUNTER0_SELECT` field set. The covered address blocks are the tail of command-processor RS64 state, `gc_gl1dec`, `gc_chdec`, `gc_gl2dec`, `gc_gl1hdec`, `gc_perfddec`, and the first part of `gc_perfsdec`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU DRM graphics-core metadata. It does not implement Ceph or distributed filesystem logic.

## Purpose

`gc_11_5_0_sh_mask.h` supplies bit layouts for GC 11.5.0 graphics hardware. Driver code pairs these macros with register offsets from `gc_11_5_0_offset.h` and typically consumes them through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`.

This chunk covers these main hardware surfaces:

- CP graphics RS64 general-purpose, instruction-pointer, pending-interrupt, data-cache aperture, and interrupt fields.
- GL1 cache/decode controls and status, including arbitration, DRAM burst behavior, fine-grain clock-gating overrides, UTCL0 controls, retry knobs, and status flags.
- CH decode/channel cache controls and status, including arbitration, burst controls, client free-delay, FGCG overrides, and CHC request counters.
- GL2 cache/decode controls, status, address matching, writeback/invalidate, soft reset, CM control/stall fields, loopback counter data/select registers, configuration, discard-stall, GL2A address matching, priority, disable, and response throttling.
- GL1H arbitration and burst controls/status.
- Performance counter data registers for CP, GRBM, GE, PA, SPI, PC, SQ, SQG, SX, GCEA, GDS, TA, TD, TCP, GL2C, GL2A, GL1C, CHC, CB, DB, RLC, RMI, GCR, PA_PH, UTCL1, GL1A, GL1H, and CHA blocks.
- Performance counter select/control registers for CP, GRBM, GE1, GE2, PA_SU, PA_SC, and the first SPI counter.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask inside the 32-bit register value.
- Matching register addresses live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`.
- Consumers generally combine these macros with `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32*`, `WREG32*`, and command-stream/register dump tooling.

Important register groups in this chunk include:

- `CP_GFX_RS64_GP*`, `CP_GFX_RS64_INSTR_PNTR*`, and `CP_GFX_RS64_PENDING_INTERRUPT*`: command-processor RS64 micro-engine state, including return addresses, read/write selector fields, stack pointers, scratch data, halted-state bits, instruction pointers, and interrupt state.
- `CP_GFX_RS64_DC_APERTURE0_*` through `CP_GFX_RS64_DC_APERTURE15_*` for both aperture banks 0 and 1: data-cache aperture base/mask/control triplets. The control registers expose `VMID` and `BYPASS_MODE` bits.
- `CP_GFX_RS64_INTERRUPT1`: per-bit interrupt fields such as `EXCP`, `HOST`, `DOORBELL`, `MC_WRREQ_ERR`, and `FAULT`.
- `GL1_ARB_CTRL`, `GL1C_CTRL`, `GL1C_STATUS`, `GL1C_UTCL0_CNTL1`, `GL1C_UTCL0_CNTL2`, `GL1C_UTCL0_STATUS`, `GL1C_UTCL0_RETRY`, and `GL1C_CTRL2`: GL1 arbitration, clock-gating, cache enable/reset/invalidating, status, client and probe FIFO state, fault-stall, response scheduling, request miss behavior, and retry controls.
- `CH_ARB_CTRL`, `CHA_CLIENT_FREE_DELAY`, `CHI_CHR_REP_FGCG_OVERRIDE`, `CHC_CTRL`, and `CHC_STATUS`: channel/decode arbitration and CHC request/status fields.
- `GL2C_CTRL*`, `GL2C_STATUS`, `GL2C_ADDR_MATCH_*`, `GL2C_WBINVL2`, `GL2C_SOFT_RESET`, `GL2C_CM_CTRL*`, `GL2C_CM_STALL`, `GL2C_LB_*`, `CC_GC_GL2C_CONFIG`, and `GL2C_DISCARD_STALL_CTRL`: GL2 cache behavior, reset, invalidation, address matching, cache-management control, loopback counter reads, configuration, and discard-stall handling.
- `GL2A_*`: GL2A address-match, priority, enable/disable, and response-throttle fields.
- `*_PERFCOUNTER*_LO` and `*_PERFCOUNTER*_HI`: data registers for low/high halves of hardware performance counters. Most expose a full-width `PERFCOUNTER` field.
- `TCP_PERFCOUNTER_FILTER`, `TCP_PERFCOUNTER_FILTER2`, and `TCP_PERFCOUNTER_FILTER_EN`: TCP performance counter filtering by shader array, WGP/SIMD, VMID, mode, slot, client, bank, request/coherency type, and enable mask.
- `*_PERFCOUNTER*_SELECT` and `*_SELECT1`: event-select and mode registers. The common layout packs `PERF_SEL0`/`PERF_SEL1` in bits 0-9 and 10-19, `CNTR_MODE` in bits 20-23, and `PERF_MODE*` in high nibbles; the companion `SELECT1` registers carry `PERF_SEL2`/`PERF_SEL3` and mode fields.
- `CP_PERFMON_CNTL` and CP latency/window select registers: control CP performance monitoring, including clock gating, counter halt, and windowing/latency-stat source selection.
- `CP_DRAW_OBJECT*`, `CP_DRAW_WINDOW_*`, and `CP_DRAW_WINDOW_CNTL`: draw/object count and draw-window performance filtering controls.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is:

1. GC 11.5.0 driver code includes the offset and shift/mask headers for the active ASIC.
2. A caller selects a register offset from `gc_11_5_0_offset.h`.
3. It uses field masks from this file with `REG_SET_FIELD` or `REG_GET_FIELD` to compose, update, or decode the register value.
4. The value is written or read through SOC15 MMIO helpers, indexed register helpers, RLC-safe accessors, command-stream packets, debugfs/register-dump paths, or profiling tools.

For cache-control registers, higher-level AMDGPU code sequences reset, invalidate, clock-gating, retry, and throttle writes around GPU init, suspend/resume, reset, or diagnostics. For performance counters, profiling code programs select/filter registers, starts or freezes counters, then reads low/high data registers. For RS64 state, register dump and command-processor control paths observe or program the micro-engine scratch, aperture, interrupt, and instruction-pointer surfaces. This file only provides bit positions and masks; ordering, waits, W1C/W1S behavior, privilege rules, and side effects are owned by hardware documentation and the driver call sites.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- RS64 GP, instruction pointer, pending interrupt, aperture, and interrupt registers are CP micro-engine state. Some fields are software-programmed configuration, while others reflect hardware-updated execution or interrupt status.
- RS64 data-cache aperture base/mask/control state persists until explicitly reprogrammed or reset. The `VMID` and `BYPASS_MODE` fields affect which virtual address context and translation behavior is used for RS64 data-cache aperture accesses.
- GL1, CH, GL2, GL2A, and GL1H control registers persist as cache/decode configuration until reset or reprogramming. Status registers can change as shader, cache, and memory traffic runs.
- GL2 invalidation, writeback, soft-reset, discard-stall, and CM stall fields are side-effect-prone control surfaces even though this generated header does not annotate access semantics.
- Performance counter select/filter/control registers persist as profiling configuration until cleared, overwritten, context-switched, reset, or power-gated. Counter data registers are hardware-updated while their selected counters are active.
- Low/high counter pairs represent wider counter state split across two 32-bit registers. Readers need a coherent sampling strategy outside this header.

Reserved or `RESERVED` fields appear throughout the range. Callers should preserve them in read-modify-write sequences unless an authoritative full-register value is being emitted.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which supplies the corresponding `reg*` register offsets and base-index metadata. This shift/mask header must remain synchronized with that offset header and AMD's generated GC 11.5.0 register database.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`, which includes `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h` and uses the generated masks through `REG_SET_FIELD` and `REG_GET_FIELD` for GCVM/gfxhub programming and fault decoding.
- Common AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15_PREREG`, which rely on the generated `__SHIFT` and `_MASK` names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h`, which carries performance event enumerations such as GL2C performance selectors used with the `*_PERFCOUNTER*_SELECT` fields represented here.
- Profiling, debugfs, performance monitoring, and register-dump tooling that programs or decodes `CPG/CPC/CPF`, `GRBM`, `GE`, `PA`, `SPI`, `TCP`, `GL2`, and related performance counters.
- ASIC bring-up, reset, suspend/resume, and power-management paths that may need cache-control and clock-gating fields from GL1, CH, GL2, and GL1H blocks.

Behaviorally, this chunk sits at the boundary between command-processor RS64 state, graphics cache/decode control, address matching/throttling, and the GC performance-monitoring fabric.

## Risks And Edge Cases

- Generated-header drift is the central risk. A bad shift or mask can compile cleanly while programming the wrong hardware bits.
- The chunk begins mid-register. The `CP_GFX_RS64_GP0_HI0__M_RET_ADDR__SHIFT` definition is in the previous chunk, while this chunk starts with its mask. File-level research must reconcile that artificial boundary.
- RS64 GP and instruction-pointer fields are low-level CP state. Mis-decoding them can confuse diagnostics; misprogramming them can affect CP micro-engine execution, stack handling, interrupt delivery, or aperture access.
- Aperture base/mask/control triplets are highly repetitive across 16 apertures and two banks. Copy/paste or generation errors can alias VMIDs, bypass behavior, or aperture ranges in ways that only show for specific aperture indices.
- GL1/GL2/CH reset, invalidation, retry, and clock-gating controls can cause hangs, stale cache contents, bad retry behavior, or power/performance regressions if masks do not match the ASIC.
- Status registers often contain transient, latched, or clear-sensitive bits. This header does not encode whether fields are read-only, write-one-to-clear, sticky, or side-effecting.
- GL2 address-match and size masks may have implicit address granularity. Consumers must apply the hardware-defined address units rather than treating every field as byte-addressed.
- Performance counter select fields are dense and repeated. Wrong `PERF_SEL*`, `CNTR_MODE`, or `PERF_MODE*` masks can silently measure the wrong event, combine wrong lanes, or make profiling data incomparable across ASICs.
- Low/high performance counter reads can race counter updates. The header does not provide latching or read-order guarantees.
- `TCP_PERFCOUNTER_FILTER` has many narrow fields for shader-array, WGP, SIMD, VMID, slot, client, bank, request, and coherency selection. An off-by-one shift can make profiling look plausible while filtering an unintended workload or VMID.
- The range ends just after `SPI_PERFCOUNTER0_SELECT`; subsequent chunks own the remaining SPI select registers and other performance select families. Merge lanes should avoid claiming this chunk covers the full `gc_perfsdec` block.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware-oriented runtime signals:

- Build AMDGPU code that includes `gfxhub_v11_5_0.c` and the GC 11.5.0 register headers. Missing or renamed macros should surface at compile time.
- Mechanically compare this range against AMD's authoritative GC 11.5.0 register database. Each complete register in the range should have matching `__SHIFT` and `_MASK` entries.
- Cross-check every register family against `gc_11_5_0_offset.h` for matching `reg*` offsets and base indices, especially repeated RS64 aperture and performance counter families.
- Run static mask sanity checks: masks should align with shifts, full-width fields should use `0xFFFFFFFFL`, repeated aperture/control blocks should be structurally identical, and common performance select layouts should match across `CPG/CPC/CPF`, `GRBM`, `GE`, `PA`, and `SPI`.
- Exercise GPU init, reset, suspend/resume, and gfxhub fault-handling paths on GC 11.5.0 hardware. Relevant signals include successful cache setup, no unexpected protection faults, and clean reset recovery.
- Run cache/coherency stress tests that trigger GL1/GL2 invalidation, writeback, retry, and throttling behavior. Watch for stale data, VM faults, hangs, retry storms, or GL2/GL1 status errors.
- Run performance profiling that programs counters from the covered blocks, reads low/high data registers, and verifies expected event changes under controlled graphics, compute, memory, and shader workloads.
- Validate TCP performance counter filters using workloads isolated by VMID, shader array, WGP/SIMD, and request/coherency type. Expected signal is selective counter movement only for the configured filter.
- Compare register dumps from known-good GC 11.5.0 hardware or simulator traces against decoded values from these masks, focusing on CP RS64 state, GL1/GL2 status, and performance select registers.

## Cross-Chunk Notes

The previous chunk owns the beginning of the CP RS64 register definitions and includes the missing shift for the first field in this range. This chunk then completes the remaining RS64 GP/aperture/interrupt region, covers GL1/CH/GL2/GL1H cache-decode controls, covers performance counter data registers, and starts performance counter select registers through `SPI_PERFCOUNTER0_SELECT`. The next chunk should continue `gc_perfsdec` with the remaining SPI and later performance select fields. The final per-file research document should merge these artificial boundaries before describing the complete GC 11.5.0 shift/mask header.

### subset-b-002560: lines 27594-30086

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 27594-30086

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains preprocessor constants only: each hardware field is represented by a `__SHIFT` bit position and an `_MASK` value used by AMDGPU register helpers to compose or decode 32-bit register values.

The requested range contains 2,145 `#define` entries: 1,074 `__SHIFT` constants and 1,087 `_MASK` constants. The mismatch is caused by artificial chunk boundaries and by the generated layout, not by executable behavior. The first requested line starts inside `SPI_PERFCOUNTER0_SELECT` after `PERF_SEL__SHIFT` was defined on line 27593, and the final requested line stops inside `RLC_CGCG_RAMP_CTRL` before its remaining masks on lines 30087-30090.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU DRM graphics-core register metadata. It does not implement distributed filesystem logic.

## Purpose

`gc_11_5_0_sh_mask.h` supplies the bit layouts for GC 11.5.0 graphics, compute, cache, command processor, RLC, performance-monitoring, and power-management registers. Driver code pairs these constants with register offsets from `gc_11_5_0_offset.h` and uses helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, indexed-register accessors, and command-stream state programming paths.

This chunk covers several dense register families:

- Graphics and compute performance counter selector registers for SPI, primitive/parameter cache, shader queues, global shader queues, SX, GDS, TA, TD, TCP, GL2C, GL2A, GL1C, CHC, CB, DB, RMI, GCR, PA_PH, UTCL1, GL1A, GL1H, and CHA blocks.
- Counter mode/filter controls, including packed `PERF_SEL*`, `PERF_MODE*`, `CNTR_MODE`, `SPM_MODE`, `PERFCOUNT_EN`, client/instance selectors, mux selectors, block selection, start/stop controls, and result counter controls.
- SQ thread trace setup and status fields for buffer bases and sizes, trace masks, token filtering, write pointers, draw/marker counters, HP3D counters, dropped-event counts, and status/error visibility.
- RLC SPM and RSPM monitoring controls, including SPM ring base/size/writer/reader pointers, segment thresholds, global and shader-engine mux select address/data registers, accumulator data/control RAM accessors, sample thresholds, pause/status, clock counters, remote SPM request/return operations, command/ack, and spare fields.
- GRTAVFS and RTAVFS voltage/frequency register access windows, target frequency/voltage fields, soft reset, PSM and clock control, and related register status fields.
- CP hypervisor and command processor microcode windows for PFP, ME, and MEC engines, plus instruction-cache and data-cache base/bound/control fields for PFP, ME, CPC, MES, GFX RS64, and MEC paths.
- The start of the RLC decoder block, including RLC control/status, firmware version, reference and GPU clock timestamps, GPM timer and interrupt controls, jump-table restore, power-gating delay, ucode control, GPM thread controls, clock-count sampling, RLCG doorbells, 32-bit GPU clock selection, power-gating control, GPM thread priority/enable, doorbell ranges, clock-gating overrides, and CGCG/CGLS ramp controls.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or runtime branches in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register value.
- Register offsets for the same GC 11.5.0 address space live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`.
- Consumers typically compose values with `REG_SET_FIELD`, decode with `REG_GET_FIELD`, and access hardware through SOC15 MMIO helpers or command-stream packets.

Important macro families in this chunk include:

- `SPI_PERFCOUNTER*_SELECT`, `PC_PERFCOUNTER*_SELECT`, `SQ_PERFCOUNTER*_SELECT`, `SQG_PERFCOUNTER*_SELECT`, `SX_PERFCOUNTER*_SELECT`, `GDS_PERFCOUNTER*_SELECT`, `TA_PERFCOUNTER*_SELECT`, `TD_PERFCOUNTER*_SELECT`, `TCP_PERFCOUNTER*_SELECT`, `GL2C/GL2A/GL1C/GL1A/GL1H_PERFCOUNTER*_SELECT`, `CHC/CHA_PERFCOUNTER*_SELECT`, `CB_PERFCOUNTER*_SELECT`, `DB_PERFCOUNTER*_SELECT`, `RMI_PERFCOUNTER*_SELECT`, `GCR_PERFCOUNTER*_SELECT`, `PA_PH_PERFCOUNTER*_SELECT`, and `UTCL1_PERFCOUNTER*_SELECT`: packed event selector and mode fields for block-specific performance counters.
- `SPI_PERFCOUNTER_BINS` and `CB_PERFCOUNTER_FILTER`: binning and filter masks that constrain which events/fragments/samples/formats/MRT operations contribute to counters.
- `SQG_PERFCOUNTER_CTRL`, `SQG_PERFCOUNTER_CTRL2`, `SQ_PERFCOUNTER_CTRL`, and `SQ_PERFCOUNTER_CTRL2`: block selection, perfmon state, client control, token mask selection, SPM enablement, SIMD/CU/WGP/SA/SE instance selectors, and perfcounter engine gating.
- `SQ_THREAD_TRACE_BUF*_BASE`, `SQ_THREAD_TRACE_BUF*_SIZE`, `SQ_THREAD_TRACE_CTRL`, `SQ_THREAD_TRACE_MASK`, `SQ_THREAD_TRACE_TOKEN_MASK`, `SQ_THREAD_TRACE_WPTR`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_STATUS2`, and thread-trace counter registers: shader trace buffer placement, capture filters, token filters, wrap/finish/status bits, and event counters.
- `GCEA_PERFCOUNTER*_CFG`, `GCEA_PERFCOUNTER2_MODE`, and `GCEA_PERFCOUNTER_RSLT_CNTL`: GCEA counter configuration, enable/clear, selection ranges, compare values/modes, and result-control fields.
- `RLC_SPM_*`: streaming performance monitor ring, mux, accumulator, pause, status, clock-count, and remote SPM request/return field definitions.
- `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER0_SELECT`, and `RLC_PERFCOUNTER1_SELECT`: RLC-level perfmon enable and event selection.
- `GRTAVFS_*` and `RTAVFS_*`: register-window address/data/control/status fields for adaptive voltage/frequency control and target frequency/voltage programming.
- `CP_HYP_*_UCODE_*`, `CP_*_UCODE_*`, `CP_ME_RAM_*`: command processor microcode and ME RAM address/data windows.
- `CP_PFP_IC_*`, `CP_ME_IC_*`, `CP_CPC_IC_*`, `CP_MES_IC_*`, `CP_MES_DC_*`, `CP_GFX_RS64_DC_*`, `CP_MEC_DC_*`, and corresponding base/bound/control registers: instruction/data cache base address, VMID, cache policy, execute-disable, address-clamp, invalidate, and prime-status fields.
- `RLC_CNTL`, `RLC_STAT`, `RLC_GPM_TIMER_*`, `RLC_INT_STAT`, `RLC_MGCG_CTRL`, `RLC_UCODE_CNTL`, `RLC_CLK_COUNT_*`, `RLC_RLCG_DOORBELL_*`, `RLC_PG_CNTL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL`: low-level RLC control, interrupts, clocks, doorbells, power gating, and clock gating.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select GC 11.5.0 register definitions for the active ASIC or for a shared GC 11.x path.
2. Pair a register address from `gc_11_5_0_offset.h` with the field layout from this header.
3. Use a register helper to insert or extract field values.
4. Perform MMIO, indexed-register, RLC-safe, KIQ, or command-stream register access in the surrounding driver code.

For performance monitoring, higher-level code chooses a hardware block and event IDs, writes the relevant `*_PERFCOUNTER*_SELECT` fields, configures counter mode/filtering, optionally enables SPM capture through `SPM_MODE` or RLC SPM registers, starts capture, reads counters or SPM ring data, then disables or reconfigures counters.

For SQ thread trace, the surrounding trace/debug path programs buffer base/size registers, masks target shader engines/arrays/CUs/SIMDs/waves, configures token filtering and capture behavior, starts tracing, watches status/write-pointer fields, and collects trace buffer contents. This header only names the bit layout; it does not provide the sequencing, synchronization, or ownership rules.

For CP microcode and cache registers, firmware-loading and engine-init code writes address/data windows for PFP/ME/MEC microcode or ME RAM, programs IC/DC bases and bounds, sets VMID/cache policy/execute-disable bits, and requests instruction-cache invalidation or priming. The cache-control fields here are side-effect sensitive, but the header does not encode waits or completion polling.

For RLC and GRTAVFS, driver power-management and firmware-control paths read or write control/status registers, configure timers and interrupts, sample clock counters, set doorbell modes and ranges, enable or disable clock/power gating, and interact with voltage/frequency target windows. The exact order is owned by the RLC, SMU, gfx, and power-management code.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state in GC 11.5.0 registers:

- Performance counter selector and control registers persist until the driver reprograms them, resets the engine, changes context/state where applicable, or power management loses/restores the block state. Counter results and status fields can change continuously while workloads run.
- SPM ring fields describe GPU memory addresses, ring sizes, read/write pointers, segment sizes, mux selectors, accumulator RAM access, pause state, and clock-count sampling. These values influence DMA-like performance data capture into memory and must agree with allocated buffers and VMID/addressing setup.
- SQ thread trace fields describe trace buffers, capture masks, token masks, write pointers, and status bits. Some fields are software-programmed configuration; others are hardware-updated status/counters.
- GRTAVFS and RTAVFS fields represent an indirect register access window plus voltage/frequency targets and control bits. Their effects persist in the adaptive voltage/frequency subsystem until changed, reset, or overridden by firmware/power-management policy.
- CP microcode address/data windows, ME RAM address/data windows, and cache base/bound/control registers affect command processor firmware storage and instruction/data fetch behavior. Base and bound fields usually carry address alignment/unit constraints not visible from the mask name alone.
- RLC control, clock, timer, interrupt, doorbell, power-gating, and clock-gating registers describe persistent firmware/engine state. Some status/interrupt/clear fields may be latched, write-one-to-clear, or read-sensitive according to hardware documentation; this generated header does not mark those access semantics.

Reserved fields appear throughout the range. Callers should preserve reserved bits on read-modify-write unless they are emitting a documented full-register value from an initialization table.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which supplies matching register offsets. The shift/mask file and offset file must remain synchronized with the same GC 11.5.0 register database.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`, which includes both `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h` and uses GC register field helpers for GFXHUB VM/fault handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`, which declares GC 11.5.x firmware names for PFP, ME, MEC, and RLC. The CP and RLC register families in this chunk are part of the same hardware initialization surface even where this exact generated header is included indirectly or shared through common GC 11 code paths.
- Common AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, KIQ-safe accessors, and debug/perfmon register paths.
- Profiling and tracing consumers that program SQ/SQG/SPI/cache/block performance counters, RLC SPM, and SQ thread trace registers.
- Firmware loading and engine setup paths for PFP, ME, MEC, MES, CPC, and RS64 cache/register state.
- Power-management and clock-gating paths coordinating RLC, SMU, GRTAVFS/RTAVFS, CGCG/CGLS, MGCG, dynamic/static WGP power gating, and clock-count sampling.

Behaviorally, this chunk sits at the boundary between performance observability, shader tracing, command processor firmware/cache setup, low-level RLC firmware services, and graphics-core clock/power control.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but writes or decodes the wrong hardware bits.
- The chunk begins and ends mid-register. The previous chunk owns `SPI_PERFCOUNTER0_SELECT__PERF_SEL__SHIFT`; the next chunk owns the remaining `RLC_CGCG_RAMP_CTRL` masks and subsequent dynamic power-gating fields. File-level research must merge these boundaries before making complete register-family claims.
- Repeated performance counter layouts are copy-sensitive. A single typo in `PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `CNTR_MODE`, or `PERF_MODE*` can corrupt only one counter lane or one block, which may escape broad build testing.
- SPM and thread trace fields are buffer-address sensitive. Incorrect base, size, write-pointer, segment, or mux fields can cause lost samples, overwritten memory, invalid traces, or GPU faults during profiling.
- Instance selector fields such as SE/SA/WGP/CU/SIMD/wave and global/instance mux selectors can make counters appear valid while measuring the wrong hardware instance.
- CP cache base and bound fields likely use aligned address units. Misinterpreting low/high address masks, VMID fields, execute-disable bits, or cache policy fields can cause firmware fetch failures, command processor hangs, or security/isolation regressions.
- Cache operation bits such as `INVALIDATE_CACHE`, `PRIME_ICACHE`, completion bits, and primed status are ordering-sensitive. The header provides masks but not the required polling or wait sequence.
- RLC interrupt/status/clear fields can be access-sensitive. Using masks without respecting W1C, latched, or firmware-owned semantics can lose interrupts or wedge low-level firmware coordination.
- Doorbell control/range/data fields affect RLCG communication. Bad mode, ID, valid, or address-range fields can drop firmware doorbells, accept unexpected doorbells, or break virtualization/resource isolation.
- RLC power-gating and clock-gating fields interact with SMU handshakes, MGCG/CGCG/CGLS controls, low-voltage mode, and per-WGP gating. Incorrect masks may show up as intermittent hangs, resume failures, performance regressions, or broken clock/power reporting rather than immediate compile failures.
- GRTAVFS and RTAVFS target frequency/voltage fields are power-management sensitive. Incorrect access-window or target field definitions can create unstable voltage/frequency programming or ineffective power policy changes.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and runtime hardware coverage:

- Build AMDGPU with GC 11.5 support enabled. Missing or renamed macros should surface in `gfxhub_v11_5_0.c`, common GC 11 code, perfmon/debug paths, firmware setup, and RLC/power-management code.
- Mechanically compare this range against the authoritative GC 11.5.0 register database. Check that complete registers in the range have aligned `__SHIFT` and `_MASK` pairs and that repeated counter families are structurally consistent.
- Cross-check every register family in this chunk against `gc_11_5_0_offset.h` for matching register offset names.
- Run static mask sanity checks: masks should align with shifts, full-width fields should use `0xFFFFFFFFL`, reserved fields should cover the expected holes, and repeated `*_PERFCOUNTER*_SELECT` families should share identical layouts where the hardware block names imply repetition.
- Exercise graphics/compute performance counter collection across SPI, PC, SQ/SQG, SX, GDS, TA/TD/TCP, GL1/GL2, CB/DB, RMI/GCR, PA_PH, UTCL1, and CH blocks. Relevant signals include nonzero counters under targeted workloads, correct block/instance selection, clean start/stop, and no GPU reset.
- Exercise RLC SPM capture with valid and boundary ring sizes, segment thresholds, mux settings, pause/resume, accumulator modes, and clock-count sampling. Expected signals are coherent sample buffers, stable write/read pointers, and no memory faults.
- Exercise SQ thread trace with multiple shader-engine/array/CU masks, token masks, buffer sizes, wrap modes, draw/marker workloads, and high event pressure. Watch for dropped-count behavior, status flags, and trace decodability.
- Exercise CP firmware loading or cache initialization paths for PFP, ME, MEC, MES/CPC/RS64 cache bases and bounds. Expected signals include successful firmware start, cache invalidate/prime completion, no command processor hangs, and correct engine status.
- Exercise RLC timers, interrupts, GPM thread controls, doorbells, and clock-count sampling. Relevant signals include expected interrupt/status transitions and stable firmware communication.
- Exercise power and clock gating transitions, suspend/resume, runtime power management, and heavy graphics/compute workloads while toggling relevant RLC/SMU policies. Watch for hangs, clock-count anomalies, SMU handshake failures, or regressions in idle/power behavior.
- Validate GRTAVFS/RTAVFS control through power-management test paths where supported, checking that target frequency/voltage and status fields behave as expected without destabilizing the GPU.

## Cross-Chunk Notes

The previous chunk must be consulted for the first field of `SPI_PERFCOUNTER0_SELECT`; this chunk starts at `SPI_PERFCOUNTER0_SELECT__PERF_SEL1__SHIFT`. The next chunk must be consulted for the remaining masks of `RLC_CGCG_RAMP_CTRL` and the following RLC dynamic power-gating registers. The final per-file document should reconcile these artificial boundaries and describe `gc_11_5_0_sh_mask.h` as a single generated GC 11.5.0 register field map.

### subset-b-002561: lines 30087-32527

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 30087-32527

## Scope

This chunk is a generated AMD GC 11.5.0 register shift/mask header segment. It contains C preprocessor constants only: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` definitions for 32-bit graphics-core hardware registers. There are no functions, structs, enums, variables, callbacks, allocations, locks, or executable branches in the selected range.

The requested slice contains 2,164 `#define` entries: 1,090 shift definitions and 1,074 mask definitions across 268 visible register groups. The count mismatch is caused by chunk boundaries. The first requested line starts at the tail of `RLC_CGCG_RAMP_CTRL` with only mask definitions; the corresponding shift definitions are immediately before this chunk. The last requested line stops inside `GFX_ICG_GL2A_CTRL` after `CLIENT14_OVERRIDE__SHIFT`, before the remaining shift and mask entries for that register.

Although the repository path is under `ceph-client`, this source is AMDGPU DRM graphics hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_11_5_0_sh_mask.h` supplies symbolic bit layouts for GC 11.5.0 registers. Consumers pair these macros with register offsets from `gc_11_5_0_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_FIELD15` to compose or decode register values.

This chunk is centered on RLC control/status and graphics power-control metadata:

- RLC clock-gating and power-gating controls: CGCG ramp masks at the boundary, dynamic/static WGP power-gating status/request registers, delay controls, always-on WGP mask, max powered-up WGP count, auto power-gating thresholds, and RLC memory light/deep-sleep controls.
- RLC SerDes and GPM/SRM access: SerDes read indices/data, target/busy masks for center hubs and shader engines, GPM general-purpose registers, GPR scratch registers, SRM command/status/index/data windows, SRM GPM command/abort controls, and save/restore copy command fields.
- RLC interrupt, error, and status groups: GPM interrupt disable/force/status, legacy interrupt disable bits, pace timer interrupt/status/disable/control, CP stat invalidation status/control, SPM/UTCL1/GPM UTCL1 status and error fields, R2I controls, GPM status, safe-mode status, and spare interrupt fields.
- RLC profiling and performance blocks: shader performance profiling (`RLC_SPP_*`) controls, shader-profile enable masks for shader engines and wave slots, SSF capture and thresholds, inflight readback, profile info, global shader IDs, PVT statistics, CAM access registers, SPM sample and MC/int controls, and SPM delay indirect address/data windows.
- RLC doorbells and embedded-controller interfaces: RLCP and XT doorbell ranges/control/status/data, CPAXI doorbell monitor fields, LX6/XT core status/interrupt/fault/reset-vector fields, XT interrupt vector force/clear/mux controls, and SMU/RLC command, response, argument, and safe-mode message registers.
- IMU boot and power-state metadata: IMU bootload address/size, throttle/early MGCG controls, and reset-vector bits for cold boot, VDDGFX, fast GFXOFF, and full GFXOFF exits.
- GC power decoder clock-gating controls: TCC disable masks and many CGTT/ICG override registers for SPI, PC, BCI, VGT, IA, WD, GS/NGG, PA, SC, SQ, SQG, ALU/TEX/LDS/SQ clocks, SP, SX, TA, TD, GDS, DB, CB, and the beginning of GL2A.

## Important APIs, Types, And Macros

There are no callable APIs or local C types. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- Matching offsets live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`.

Important register families in this chunk include:

- `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_WGP_STATUS`, `RLC_PG_ALWAYS_ON_WGP_MASK`, `RLC_MAX_PG_WGP`, `RLC_PG_DELAY`, `RLC_PG_DELAY_3`, and `RLC_AUTO_PG_CTRL`: WGP-level power gating, idle thresholds, propagation delays, memory sleep delay, and auto wake/save behavior.
- `RLC_SERDES_RD_INDEX`, `RLC_SERDES_RD_DATA_0..3`, `RLC_SERDES_MASK`, `RLC_SERDES_CTRL`, `RLC_SERDES_DATA`, and `RLC_SERDES_BUSY`: RLC SerDes read/write routing, broadcast, register address, target mask, read FIFO, and pending/busy indicators.
- `RLC_GPM_GENERAL_0..16`, `RLC_GPR_REG1`, `RLC_GPR_REG2`, `RLC_SRM_CNTL`, `RLC_SRM_GPM_COMMAND_STATUS`, `RLC_SRM_INDEX_CNTL_ADDR_0..7`, `RLC_SRM_INDEX_CNTL_DATA_0..7`, `RLC_SRM_STAT`, `RLC_SRM_GPM_COMMAND`, and `RLC_SRM_GPM_ABORT`: general-purpose mailboxes and SRM/GPM save-restore machinery.
- `RLC_GPM_UTCL1_CNTL_0`, `RLC_GPM_UTCL1_CNTL_1`, `RLC_SPM_UTCL1_CNTL`, `RLC_UTCL1_STATUS`, `RLC_UTCL1_STATUS_2`, `RLC_SPM_UTCL1_ERROR_*`, and `RLC_GPM_UTCL1_TH*_ERROR_*`: UTCL1 control, hit/miss/status, request, miss FIFO, translation, and fault/error information for RLC GPM/SPM paths.
- `RLC_CGCG_CGLS_CTRL_3D`, `RLC_CGCG_RAMP_CTRL_3D`, `RLC_MEM_SLP_CNTL`, `RLC_POWER_RESIDENCY_*`, `RLC_CLK_RESIDENCY_*`, `RLC_DS_RESIDENCY_*`, `RLC_ULV_RESIDENCY_*`, `RLC_PCC_RESIDENCY_*`, and `RLC_GENERAL_RESIDENCY_*`: clock gating, light sleep, deep sleep, residency event counters, reference counters, selector masks, enable bits, and counter-control fields.
- `RLC_PACE_INT_STAT`, `RLC_PACE_INT_DISABLE`, `RLC_PACE_TIMER_INT_0`, `RLC_PACE_TIMER_INT_1`, and `RLC_PACE_TIMER_CTRL`: RLC pacing interrupt flags, masking, timer periods, delayed-error fields, and timer enable/state.
- `RLC_SPP_CTRL`, `RLC_SPP_SHADER_PROFILE_EN`, `RLC_SPP_SSF_CAPTURE_EN`, `RLC_SPP_SSF_THRESHOLD_*`, `RLC_SPP_INFLIGHT_RD_*`, `RLC_SPP_PROF_INFO_*`, `RLC_SPP_GLOBAL_SH_ID*`, `RLC_SPP_STATUS`, `RLC_SPP_PVT_STAT_*`, `RLC_SPP_PVT_LEVEL_MAX`, `RLC_SPP_STALL_STATE_UPDATE`, `RLC_SPP_PBB_INFO`, `RLC_SPP_RESET`, `RLC_SPP_CAM_*`, and `RLC_SPP_CAM_EXT_*`: shader profiling, power profiling, scan/filter capture, private statistics, CAM windows, reset, and stall-update controls.
- `RLC_RLCP_DOORBELL_*`, `RLC_XT_DOORBELL_*`, and `RLC_CPAXI_DOORBELL_MON_*`: doorbell range sizing, enable/offset fields, source pointer selection, hit status, data readback, and CPAXI monitoring.
- `RLC_XT_CORE_STATUS`, `RLC_XT_CORE_INTERRUPT`, `RLC_XT_CORE_FAULT_INFO`, `RLC_XT_CORE_ALT_RESET_VEC`, `RLC_XT_INT_VEC_FORCE`, `RLC_XT_INT_VEC_CLEAR`, `RLC_XT_INT_VEC_MUX_SEL`, and `RLC_XT_INT_VEC_MUX_INT_SEL`: embedded XT/LX6 controller status, interrupt, fault, reset-vector, and interrupt-vector routing fields.
- `SMU_RLC_RESPONSE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `RLC_RLCV_COMMAND`, `RLC_SMU_MESSAGE*`, `RLC_SMU_COMMAND`, and `RLC_SMU_ARGUMENT_1..5`: command/response and safe-mode interfaces between RLC, RLCV, and SMU firmware-controlled paths.
- `RLC_IMU_BOOTLOAD_ADDR_*`, `RLC_IMU_BOOTLOAD_SIZE`, `RLC_IMU_MISC`, and `RLC_IMU_RESET_VECTOR`: IMU firmware bootload address/size and reset-vector metadata.
- `CGTS_TCC_DISABLE`, `GFX_ICG_*`, `CGTT_*`, `SQ_*_CLK_CTRL`, `ICG_*`, `TA_CGTT_CTRL`, `DB_CGTT_CLK_CTRL_0`, and `GFX_ICG_CB_CTRL`: per-block clock gating, soft-stall/soft-override, register override, off-hysteresis, on-delay, perf-enable, and group override definitions.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. GC 11.5.0 code includes `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h`.
2. The caller chooses a register offset, usually through a `reg*` macro and SOC15 helper.
3. The caller builds or decodes a `u32` register value using `REG_SET_FIELD`, `REG_GET_FIELD`, direct masks, or direct shifts.
4. Ordered MMIO access, polling, firmware messaging, reset sequencing, and power-domain ownership are handled outside this header.

In this tree, the observed direct GC 11.5.0 include user is `drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`, which uses this generated namespace for VM hub setup and fault-status decoding. The RLC and clock-gating register names in this chunk also match broader AMDGPU GFX 11 patterns used by generic `gfx_v11_0.c` and newer GFX code: safe-mode entry/exit writes use `RLC_SAFE_MODE`-style `CMD` and `MESSAGE` fields, SPM VMID setup uses `RLC_SPM_MC_CNTL` fields, and clock-gating setup toggles RLC/CGTT/MGCG override fields around power-management transitions. Those generic files do not directly include this GC 11.5.0 header, but they show the intended semantic use of this register class.

The generated masks do not encode legal ordering, polling delays, write-one-to-clear semantics, self-clearing requests, read-only status, firmware-owned registers, SR-IOV restrictions, or power-domain accessibility. Those rules must come from the consuming code and hardware programming guide.

## State And Persistence Behavior

The file stores no software state and persists nothing. It names hardware-visible state whose lifetime is controlled by the GPU, firmware, reset domains, power gating, and driver reinitialization.

Represented state includes:

- WGP power-gating state, request masks, always-on masks, maximum powered WGP count, auto power-gating thresholds, and RLC memory light/deep-sleep state.
- RLC SerDes routing and busy/read-pending state across center hubs and shader-engine targets.
- RLC GPM/SRM scratch, command, FIFO, auto-increment, and copy state used for register save/restore and firmware-managed data movement.
- RLC interrupt masks, forced interrupts, pace timers, spare interrupts, CP stat invalidation state, and interrupt-handler client status.
- UTCL1 status and fault/error state for GPM/SPM accesses, including request counters, miss FIFO status, fault IDs, and client/status flags.
- SPM/SPP profiling state, including enabled shader-engine/wave masks, sample counters, capture thresholds, inflight readback state, profile info, CAM data windows, and PVT statistics.
- Doorbell range, enable, offset, source, hit, and data state for RLCP and XT interfaces, plus CPAXI doorbell monitor readback.
- RLC/SMU/RLCV command and response mailboxes, safe-mode request/response bits, IMU bootload metadata, and IMU reset-vector bits used across boot and low-power exits.
- Power/clock-gating overrides for graphics pipeline blocks. Many fields named `SOFT_OVERRIDE`, `SOFT_STALL_OVERRIDE`, `GRP_OVERRIDES`, `REG_OVERRIDE`, `ON_DELAY`, and `OFF_HYSTERESIS` affect whether block-level clocks can gate, when gating occurs, and whether perf/debug logic forces clocks on.

Some registers are configuration that persists until reset or reprogramming; others are live status, counters, command triggers, firmware mailboxes, or sticky error/interrupt state. The macro names alone do not identify volatility or side effects. Reserved and `UNUSED` fields should be preserved on read-modify-write unless an ASIC programming table explicitly owns the full register value.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which supplies matching register offsets and address-block placement. The shift/mask header must stay synchronized with that offset header and AMD's authoritative GC 11.5.0 register database.

Observed direct include user:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`

Semantic integration points for this chunk include:

- RLC firmware and microcontroller bring-up, including RLC/SMU/RLCV messaging, safe-mode transitions, IMU bootload state, and GFXOFF or VDDGFX exit handling.
- Runtime power management, clock gating, clock-stop controls, memory light/deep sleep, power residency counters, and block-specific clock-gating overrides.
- GPU reset, suspend/resume, and recovery paths that need to reinitialize RLC-managed state, doorbell ranges, safe-mode state, SPM/SPP profiling controls, and clock-gating overrides.
- Profiling and diagnostics through RLC SPM/SPP counters, shader-profile enable masks, PVT statistics, CAM windows, residency counters, GFX IH client status, and UTCL1 error/status registers.
- Firmware or low-level driver paths that use SRM/GPM register save/restore windows and GPM general-purpose mailboxes.
- Doorbell, CPAXI, and embedded-controller interrupt routing between host, RLC, RLCP, XT/LX6 controller logic, and SMU-owned firmware flows.
- Common AMDGPU register helper infrastructure for SOC15 addressing and field packing/unpacking.

Mixing this GC 11.5.0 mask header with another GC generation's offset header can compile but program the wrong hardware bits.

## Risks And Edge Cases

- Generated-header drift is high impact. A wrong shift or mask can silently alter firmware commands, power-state transitions, profiling setup, doorbell routing, or clock-gating behavior.
- The chunk boundaries are artificial. This slice begins with only `RLC_CGCG_RAMP_CTRL` masks and ends before `GFX_ICG_GL2A_CTRL` is complete; adjacent chunk documents are required before making complete file-level claims about those register groups.
- RLC safe-mode, SMU message, RLCV command, and SRM/GPM command fields are side-effect sensitive. Whole-register writes or stale command bits can trigger firmware actions, fail to enter/exit safe mode, or abort save/restore operations unexpectedly.
- Power-gating and clock-gating fields can create intermittent hangs or performance regressions rather than immediate build failures. Bad WGP masks, delay fields, CGCG/CGLS thresholds, memory sleep overrides, or block-level clock overrides can break idle entry/exit, GFXOFF, profiling, or reset recovery.
- Repeated register families are copy-sensitive: `RLC_SRM_INDEX_CNTL_ADDR/DATA_0..7`, `RLC_GPM_GENERAL_*`, `RLC_SPP_PVT_STAT_0..3`, RLCP/XT doorbell data pairs, and many `CGTT_*`/`GFX_ICG_*` controls must remain structurally consistent with their offsets.
- Status, interrupt, force, disable, and command registers sit near each other. The generated header does not distinguish read-only status, write-one-to-clear, mask-disable, force, self-clearing request, or sticky error behavior.
- Address and size fields may have implicit alignment or unit semantics, such as doorbell offsets starting above low bits, SRM command size/start offsets, IMU bootload size width, and delay counters measured in hardware-specific units.
- Profiling fields can perturb the workload under measurement. SPM/SPP enable masks, shader-profile wave selection, CAM access, SSF capture, and PVT statistics should be synchronized with profiling ownership and power-management state.
- Firmware ownership matters. RLC, SMU, IMU, and XT/LX6 controller registers may be invalid or unsafe to access when their firmware block is halted, power gated, in reset, or owned by another virtualization function.
- Reserved and `UNUSED` masks are present throughout the clock-gating and control registers. New code should preserve them unless writing validated golden-register values.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware integration tests:

- Build and preprocess GC 11.5.0 AMDGPU paths that include `gc_11_5_0_sh_mask.h`, especially `gfxhub_v11_5_0.c`, with common SOC15 register helpers enabled.
- Mechanically compare this chunk against the authoritative GC 11.5.0 register database. Verify that complete registers in the chunk have matching shift/mask pairs and that boundary exceptions are limited to `RLC_CGCG_RAMP_CTRL` and `GFX_ICG_GL2A_CTRL`.
- Cross-check every register group in this slice against `gc_11_5_0_offset.h` for corresponding `reg*` or `mm*` offsets and correct address-block placement.
- Run static mask sanity checks: each mask should align with its shift, full-width data fields should use `0xFFFFFFFFL`, repeated SRM/GPM, doorbell, SPP, residency-counter, and clock-control families should have regular layouts.
- Exercise GPU init, suspend/resume, runtime power management, GFXOFF entry/exit, GPU reset, and recovery on GC 11.5.0-class hardware. Watch for failed safe-mode polling, RLC/SMU command timeouts, invalid IMU boot/exit behavior, and clock-gating regressions.
- Validate RLC power-gating behavior with idle and busy graphics/compute workloads. Relevant signals include WGP power status/request bits, residency counters, RLC busy/status bits, and absence of hangs during power-state changes.
- Exercise SPM/SPP profiling and shader profiling controls. Expected signals are plausible sample counts/statistics, correct VMID or shader-engine selection, working CAM readback, and no lost workload progress while profiling is enabled.
- Test doorbell paths and embedded-controller interrupt routing where supported, checking RLCP/XT doorbell hit/status/data fields, CPAXI monitor data, and XT interrupt vector force/clear behavior under controlled diagnostics.
- Inspect UTCL1 and RLC error/status registers during induced fault or debug scenarios. Fault IDs, client IDs, miss FIFO flags, and CP stat invalidation status should decode consistently with expected conditions.
- Compare clock-gating register dumps against known-good golden-register or firmware-programmed values after init, after runtime power transitions, and after reset. Regression indicators include clocks stuck forced on, clocks gating during active work, unexpected perf counter disablement, or block-specific render/compute hangs.

## Cross-Chunk Notes

The previous chunk owns the start of `RLC_CGCG_RAMP_CTRL`; this chunk starts at its mask tail and then covers the bulk of RLC power, status, profiling, firmware-message, IMU, and doorbell metadata before entering the `gc_pwrdec` clock-gating block. The next chunk should complete `GFX_ICG_GL2A_CTRL` and continue later power/clock control register definitions. The merge lane should reconcile these boundaries before producing the final per-file research document.

### subset-b-002562: lines 32528-35050

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 32528-35050

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains preprocessor constants only: hardware register fields are described as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for callers that need to pack or extract 32-bit register values.

The requested range contains 2,152 shift/mask `#define` entries. It begins in the middle of `GFX_ICG_GL2A_CTRL`: the earlier shift definitions for that register are in the previous chunk, while this chunk starts at `GFX_ICG_GL2A_CTRL__CLIENT15_OVERRIDE__SHIFT` and then carries all of the masks. It ends after `FIXED_PATTERN_PERF_COUNTER_7`; the next chunk continues with fixed-pattern counters 8-10 and LUT update status.

Although the file lives under a local `ceph-client` source mirror, this is AMDGPU DRM graphics-core metadata. It does not implement distributed filesystem or Ceph behavior.

## Purpose

`gc_11_5_0_sh_mask.h` supplies field layouts for GC 11.5.0 graphics hardware. Driver code pairs these field macros with register offsets from `gc_11_5_0_offset.h` and common AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and `SOC15_REG_OFFSET`.

This chunk covers several large register families:

- Fine-grained and medium-grained clock-gating controls for CP, CPF, CPC, RLC, scan converter/PBB, GL2, TCP, UTCL1, CHC, LDS, CHA, GL1, GCR, RMI, GRBM, GCEA, and GC/SE CAC blocks.
- Hypervisor-visible GC registers in `gc_hypdec`, including graphics pipe priority, GRBM shader-array/instance indexing and remap controls, RLC SDMA busy/status, RLC hypervisor semaphores, RLC pace interrupt/cookie state, RLC/GPM/PACE microcode and scratch address/data windows, pipe steering, and user-visible shader-array/RB/TCC disable or redundancy configuration.
- PSP-facing GC debug and data-index windows in `gc_pspdec`, including MES, MEC, and GFX RS64 data-master index/data registers plus GRBM CAM and secure-control fields.
- GFX IMU host/RLC/SOC interface registers, including C2P mailboxes 0-47, mailbox access controls, power-management IRQ control, MP1/RLC mutexes, RLC command/data/status paths, SOC access request/address/data registers, VF control, scratch registers, timestamp/offset registers, PIC interrupt controller state, IH controls, clock/doorbell/RLC clock-gating/throttle controls, DPM counters, RLC RAM access, fence/control/status, reset/power-good status, and IMU instruction/data RAM windows.
- GC CAC indirect-register metadata in `gccacind`, including CAC identification/control, full-width accumulator counters for CP, EA, UTCL2 router/VML2/walker/ATCL2, GDS, GE, PMM, GL2C, PH, SDMA, CHC, and RLC blocks.
- Clock-state transition lookup tables and counters: release-to-stall, stall-to-release, stall-to-power-break, power-break-stall-to-release, power-break-release-to-stall LUT entries, and fixed-pattern performance counters 1-7.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, callbacks, or executable branches in this range. The API surface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the register-value mask for that field.
- Matching register offsets are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`.
- Indirect CAC accumulator offsets use `ixGC_CAC_*` names in the offset header rather than direct `reg*` MMIO names.

Important field groups in this chunk include:

- `CGTT_CP_CLK_CTRL`, `CGTT_CPF_CLK_CTRL`, `CGTT_CPC_CLK_CTRL`, `CGTT_SC_CLK_CTRL3`, `CGTT_SC_CLK_CTRL4`, `GFX_ICG_*`, `GL1*`, `ICG_*`, and `GFX_ICG_UTCL1_CTRL`: clock-gating hysteresis, manual override, stall override, MGLS, and per-client/per-sub-block clock control fields.
- `GFX_PIPE_PRIORITY`, `GRBM_GFX_INDEX_SR_SELECT/DATA`, `GRBM_GFX_CNTL_SR_SELECT/DATA`, `GRBM_SE_REMAP_CNTL`, `GRBM_SA_REMAP_CNTL`, `GRBMH_WGP_REMAP_CNTL`, and `GRBMH_RB_REMAP_CNTL`: pipe priority, shader-array addressing, and physical-to-logical remap controls.
- `RLC_SDMA*_STATUS`, `RLC_SDMA*_BUSY_STATUS`, `RLC_HYP_SEMAPHORE_*`, `RLC_BUSY_CLK_CNTL`, `RLC_CLK_CNTL`, `RLC_PACE_*`, `RLC_IH_COOKIE*`, and RLC/GPM/PACE/RLCV/SRM address/data windows: RLC status, firmware windows, semaphore, interrupt-cookie, and pacing fields.
- `GL2_PIPE_STEER_*`, `GL1_PIPE_STEER`, `CH_PIPE_STEER`, `GC_USER_SHADER_ARRAY_CONFIG`, `GC_USER_PRIM_CONFIG`, `GC_USER_*_DISABLE`, `GC_USER_*_REDUNDANCY`, `CGTS_USER_TCC_DISABLE`, and `GC_USER_SHADER_RATE_CONFIG`: user-visible topology, disable, redundancy, and rate-configuration metadata.
- `CP_MES_DM_INDEX_*`, `CP_MEC_DM_INDEX_*`, `CP_GFX_RS64_DM_INDEX_*`, `CPG_PSP_DEBUG`, `CPC_PSP_DEBUG`, `GRBM_SEC_CNTL`, and `GRBM*_CAM_*`: PSP/debug data windows and secure GRBM CAM access fields.
- `GFX_IMU_C2PMSG_*`, `GFX_IMU_MSG_FLAGS`, `GFX_IMU_*ACCESS_CTRL*`, `GFX_IMU_RLC_*`, `RLC_GFX_IMU_*`, `GFX_IMU_SOC_*`, `GFX_IMU_PIC_*`, `GFX_IMU_IH_*`, `GFX_IMU_DPM_*`, `GFX_IMU_RLC_RAM_*`, `GFX_IMU_CORE_CTRL`, `GFX_IMU_RESETn`, `GFX_IMU_GFX_RESET_CTRL`, `GFX_IMU_D_RAM_*`, and `GFX_IMU_I_RAM_*`: IMU mailbox, interrupt, firmware RAM, reset, DPM, and host/RLC/SOC handshake fields.
- `GC_CAC_ID`, `GC_CAC_CNTL`, and `GC_CAC_ACC_*`: CAC block identity/control and full-width 32-bit accumulator fields.
- `RELEASE_TO_STALL_LUT_*`, `STALL_TO_RELEASE_LUT_*`, `STALL_TO_PWRBRK_LUT_*`, `PWRBRK_*_LUT_*`, and `FIXED_PATTERN_PERF_COUNTER_*`: transition-pattern lookup-table fields and fixed-pattern performance counter fields.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select GC 11.5.0 register offsets and field definitions for an ASIC in the GC 11.5 family.
2. Build a register value with field masks/shifts, usually through `REG_SET_FIELD`, or decode a readback value with `REG_GET_FIELD`.
3. Access the target register through direct SOC15 MMIO helpers, indexed register windows, RLC-safe helpers, PSP/MES/MEC data-master windows, or indirect CAC index/data paths.
4. Use the value during graphics init, clock-gating setup, power-management handshakes, reset/recovery, topology enumeration, firmware mailbox exchange, virtualization/hypervisor operations, or diagnostics.

For clock-gating registers, higher-level code decides whether blocks should be auto-gated, forced on, stalled, or overridden; these macros only define the bit layout. For GRBM and pipe-steering registers, callers select shader engines, shader arrays, render backends, TCCs, or pipes before performing targeted programming or topology reporting. For IMU registers, code writes mailbox/request/status fields in a firmware-defined sequence; this chunk does not encode those wait loops or ordering rules. For GC CAC registers, software selects an indirect accumulator and reads or configures counter/control state through the CAC index/data aperture.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- Clock-gating and ICG/CGTT override fields persist in hardware registers until changed by driver init, power-management code, firmware, reset, suspend/resume restore, or ASIC reinitialization.
- GRBM index, remap, topology, and pipe-steering fields affect which shader-engine, shader-array, workgroup-processor, render-backend, cache, or pipe instances subsequent accesses target. Some fields are global broadcast selectors; others are per-topology configuration state.
- RLC status, busy, pace, cookie, semaphore, microcode, scratch, and RAM-window fields represent firmware-visible state. Address/data windows are stateful selectors, so incorrect sequencing can read or write the wrong internal RAM or scratch location.
- PSP, MES, MEC, and GFX RS64 data-master index/data windows are mailbox-like debug or firmware access mechanisms. The selected index and data value persist as register state and may have firmware side effects.
- GFX IMU C2P mailboxes, mutexes, command/status registers, DPM counters, interrupt-controller registers, RAM windows, reset controls, and power-good fields are shared between host driver, RLC, MP1/SMU, PSP-adjacent flows, and IMU firmware. Some are software-programmed controls, some are hardware/firmware-updated status, and some are side-effectful command windows.
- GC CAC accumulator registers are counter state for graphics-core activity or power/clock accounting. The `ACCUMULATOR_31_0` fields are full 32-bit values and may roll over or be sampled/reset by firmware or driver policy.
- Stall/release/power-break LUTs and fixed-pattern performance counters are hardware tuning/measurement state for clock/power transition logic.

Reserved fields and full-register masks appear throughout this range. Callers should preserve undocumented bits during read-modify-write unless the programming sequence explicitly owns the complete register value.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which supplies the corresponding `reg*` and `ix*` offsets. The shift/mask header must remain synchronized with that offset header and AMD's source register database.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`, which directly includes both `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h`.
- Common AMDGPU register-helper infrastructure: `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, indexed MMIO helpers, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- `gfx_v11_0.c`, `gfx_v12_0.c`, `mes_v11_0.c`, `mes_v12_0.c`, and `amdgpu_amdkfd_gfx_v11.c` show the same architectural field families in use for GRBM indexing, RLC clock-gating overrides, IMU firmware access, MES/RLC setup, and KFD-specific indexed GRBM programming. GC 11.5-specific code may include fewer direct users in this mirror, but the register layouts align with those shared programming patterns.
- `imu_v11_0.c`, `imu_v11_0_3.c`, and `imu_v12_0.c` are relevant consumers for IMU mailbox/access-control/RLC-RAM patterns around registers represented in this chunk.
- PM/SMU code and firmware-interface headers expose feature flags and policy controls for GFX IMU, GC CAC, and clock/power management; this header supplies the low-level GC register field metadata those flows ultimately rely on.

## Risks And Edge Cases

- Generated-header drift is the main risk. An incorrect shift or mask will compile cleanly but program the wrong hardware bits.
- The range starts and ends mid-family. File-level research should merge adjacent chunks before making complete claims about `GFX_ICG_GL2A_CTRL` or the fixed-pattern counter and `HW_LUT_UPDATE_STATUS` families.
- Clock-gating override fields are power and liveness sensitive. Incorrect `SOFT_OVERRIDE`, `SOFT_STALL_OVERRIDE`, hysteresis, MGLS, or per-client override masks can cause hangs, clock domains stuck on/off, failed idle entry, or large power regressions.
- Repeated register families are copy-sensitive. Examples include PBB/SC clock fields, IMU C2P message registers, PIC priority registers, CAC accumulators, and transition LUT pattern slots; a one-register mismatch can affect only a narrow instance.
- GRBM index and remap fields affect addressing of per-SE/per-SA/per-instance registers. Bad masks can direct writes to the wrong shader array, accidentally broadcast writes, or misreport harvested/disabled topology.
- RLC, GPM, PACE, SRM, IMU, and PSP data windows are selector/data pairs. If field definitions or sequencing are wrong, firmware memory, scratch, or control windows can be corrupted without an obvious local failure.
- Mailbox, mutex, interrupt, and reset fields can be shared across host driver, firmware, and virtualization paths. Access-order, ownership, or stale-bit mistakes can deadlock firmware handshakes or lose interrupts.
- `GC_USER_*_DISABLE`, redundancy, pipe-steering, and shader-rate configuration fields describe hardware topology and policy. Wrong masks can expose nonexistent resources, hide available resources, or route traffic incorrectly.
- CAC accumulator and fixed-pattern counter fields may roll over, be sampled asynchronously, or have clear/update side effects outside this header. The macros do not document read-clear, latch, or sampling rules.
- LUT transition fields are compact bitfields with different widths across release/stall/power-break tables. Reusing the wrong table width can silently corrupt adjacent pattern entries.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware runtime signals:

- Build AMDGPU with GC 11.5 support. Include users such as `gfxhub_v11_5_0.c` should catch missing or renamed macros; broader GC 11 builds exercise the shared field-family conventions.
- Mechanically compare this range against the authoritative GC 11.5.0 register database. Check that masks align with shifts, full-width fields use `0xFFFFFFFFL`, and repeated families have consistent shapes.
- Cross-check every register family in this chunk against `gc_11_5_0_offset.h` for matching direct `reg*` offsets or indirect `ixGC_CAC_*` offsets.
- Run static sanity checks around boundary registers: `GFX_ICG_GL2A_CTRL` must be reconciled with the previous chunk, and fixed-pattern counters 8-10 plus `HW_LUT_UPDATE_STATUS` must be reconciled with the next chunk.
- Exercise graphics init, suspend/resume, GPU reset, and runtime power-management paths. Relevant signals are successful clock-gating enable/disable transitions, no RLC/IMU firmware timeouts, stable idle residency, and no unexpected power draw or hangs.
- Exercise GRBM-indexed register access across shader engines, shader arrays, WGPs, render backends, and harvested configurations. Expected signals include correct broadcast behavior and accurate topology reporting.
- Exercise IMU firmware loading, C2P mailbox traffic, RLC RAM access, DPM/ref-counter reads, interrupt delivery, reset sequencing, and doorbell control. Watch for mailbox timeouts, stale mutexes, missing IH/PIC interrupts, or reset failures.
- Exercise virtualization or hypervisor-facing flows where available: RLC hypervisor semaphores, secure GRBM CAM access, PSP debug windows, and user topology/remap fields.
- Read/sample GC CAC accumulators and fixed-pattern performance counters around known graphics/compute activity. Expected signals are monotonic or policy-expected counter movement, sensible rollover handling, and no access faults through the CAC indirect path.
- Run mixed graphics/compute workloads under power-management stress to expose clock-gating, pipe-steering, and transition-LUT issues that may appear only under load, idle, or rapid state transitions.

## Cross-Chunk Notes

The previous chunk owns most of `GFX_ICG_GL2A_CTRL`; this chunk begins with its final shift definition and all masks, then covers CGTT/ICG controls, GC hypervisor-visible controls, PSP windows, GFX IMU windows, CAC accumulators, transition LUTs, and fixed-pattern performance counters 1-7. The next chunk should continue fixed-pattern counters 8-10 and `HW_LUT_UPDATE_STATUS`. The final per-file document should reconcile these artificial line boundaries before describing the complete GC 11.5.0 shift/mask header.

### subset-b-002563: lines 35051-36579

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 35051-36579

## Chunk Scope

This chunk is a generated AMD GC 11.5.0 register shift/mask header segment. It contains C preprocessor constants only: `REGISTER__FIELD__SHIFT` macros and matching `REGISTER__FIELD_MASK` macros for MMIO or indexed GPU registers. There are no functions, structs, enums, variables, callbacks, allocations, locks, or executable branches.

The requested range contains 1,529 source lines and 1,275 `#define` entries: 637 shift constants and 638 mask constants. The one-extra mask is a chunk-boundary artifact: the first line is the tail mask for `FIXED_PATTERN_PERF_COUNTER_7`, whose shift definition is in the preceding chunk. This range then covers the end of fixed-pattern performance/LUT update status definitions, the complete `secacind` block in this chunk, the full visible `grtavfsind` block from `RTAVFS_REG0` through `RTAVFS_REG194`, and the `sqind` wave/debug register layouts through `SQ_WAVE_EXEC_HI`. The file ends at this chunk's final line with `#endif`.

Although the source tree path is under `ceph-client`, this is AMDGPU DRM graphics-core metadata, not distributed filesystem logic.

## Purpose

`gc_11_5_0_sh_mask.h` supplies symbolic bitfield definitions for GC 11.5.0 hardware programming. The companion `gc_11_5_0_offset.h` header provides register offsets, while this header provides the bit positions and masks consumed by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_FIELD15_PREREG`.

This particular slice names fields for:

- Fixed-pattern counters and hardware LUT update completion/error state, used by power/performance management blocks to expose pattern counter values and table-update status.
- `secacind` CAC selection and threshold registers, selecting CAC block/signal IDs and threshold values.
- `grtavfsind` RTAVFS registers, which describe real-time adaptive voltage/frequency scaling zones, CPO/ripple-counter windows, frequency/voltage-code pairs, guard bands, proportional/integral controller knobs, PSM measurement controls, CPO enable masks, live ripple counts, debug stop points, FSM status, and override/readback fields.
- `sqind` shader-queue debug and wave registers, including SQ busy status, active/valid wave masks, wave mode/status/trap state, resource allocation, outstanding instruction-buffer counters, program counter, hardware IDs, scheduler mode, scratch registers, TTMP registers, M0, and EXEC masks.

The generated macro names are part of the driver ABI for this ASIC generation. Callers depend on the exact spelling pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` when composing or decoding register values.

## Important APIs, Types, And Macros

There are no callable APIs or local types. The exported interface is the macro namespace.

Important macro families in this range:

- `FIXED_PATTERN_PERF_COUNTER_8`, `FIXED_PATTERN_PERF_COUNTER_9`, and `FIXED_PATTERN_PERF_COUNTER_10` define 17-bit `PERF_COUNTER` fields. The first line also completes `FIXED_PATTERN_PERF_COUNTER_7` from the previous chunk.
- `HW_LUT_UPDATE_STATUS` exposes per-table completion and error state for update tables 1 through 5. Each table has `*_DONE`, `*_ERROR`, and multi-bit `*_ERROR_STEP` fields.
- `SE_CAC_ID` and `SE_CAC_CNTL` define the CAC indexed-register selector and threshold layout: `CAC_BLOCK_ID`, `CAC_SIGNAL_ID`, and `CAC_THRESHOLD`.
- `RTAVFS_REG0` through `RTAVFS_REG4` define five zone start/stop count pairs.
- `RTAVFS_REG5` through `RTAVFS_REG14` define two full-width enable masks per RTAVFS zone.
- `RTAVFS_REG15` through `RTAVFS_REG18` define four frequency-count/voltage-code pairs. `RTAVFS_REG19` defines per-zone guard-band fields.
- `RTAVFS_REG20` through `RTAVFS_REG24` and `RTAVFS_REG120` define per-zone and global CPO averaging divisors, including eight intermediate divisor fields and a final divisor field.
- `RTAVFS_REG25` through `RTAVFS_REG27`, plus several `RESERVED` fields across the block, are generated full or partial reserved layouts. They still matter for preserving register width and avoiding accidental writes to undocumented bits.
- `RTAVFS_REG28` through `RTAVFS_REG30` define zone intercept values.
- `RTAVFS_REG31` through `RTAVFS_REG42` define CPO clock dividers and RTAVFS FSM timing counters for startup, idle, reset, CPO start/stop, ripple-counter start/done, final-result ready, voltage-code ready, target-voltage ready, and wait-for-ack phases.
- `RTAVFS_REG43` through `RTAVFS_REG48` define proportional/integral control coefficients, voltage anchors, binary-search and hardware-calibration controls, VR enable/bleed controls, voltage-code overrides, low-power and sensing bits, PI anti-windup/shift/error controls, PI output limits, loop iterations, and error thresholds.
- `RTAVFS_REG49` through `RTAVFS_REG53` define PSM controls and measured min/max/average values for VDD and VREG paths.
- `RTAVFS_REG54` through `RTAVFS_REG117` define CPO0 through CPO63 start/stop counter windows.
- `RTAVFS_REG118` and `RTAVFS_REG119` provide full-width CPO enable masks for the 64 CPO counters.
- `RTAVFS_REG121` exposes live zone-in-use bits and an `RTAVFSERRORCODE`.
- `RTAVFS_REG122` through `RTAVFS_REG185` define CPO0 through CPO63 ripple-count readback fields.
- `RTAVFS_REG186` and `RTAVFS_REG187` define target/current frequency-count overrides and selector bits.
- `RTAVFS_REG189` through `RTAVFS_REG194` define PI/binary-search voltage-code readback, VDD regulator state, loop/debug controls, FSM stop-at-state controls, scaled/final CPO count readbacks, FSM state, and selected ripple-count readback.
- `SQ_DEBUG_STS_LOCAL` and `SQ_DEBUG_CTRL_LOCAL` define SQ local debug busy bits and a small control field.
- `SQ_WAVE_ACTIVE` and `SQ_WAVE_VALID_AND_IDLE` define wave-slot bitmaps.
- `SQ_WAVE_MODE` defines floating-point rounding/denormal controls, DX10 clamp, IEEE mode, LOD clamp, trap-after-instruction enable, exception enables, wave-end, FP16 overflow, and performance-disable fields.
- `SQ_WAVE_STATUS` defines wave condition/status bits including SCC, SPI/user priority, privilege, trap/thread-trace enables, export readiness, EXEC/VCC zero flags, barrier/threadgroup state, halt/trap, valid/ECC/perf bits, fatal halt, no-VGPR state, LDS parameter readiness, GS allocation/export requirements, idle, and scratch enable.
- `SQ_WAVE_TRAPSTS` defines exception, save-context, illegal instruction, high exception bits, buffer OOB, host trap, wave-start/end, performance snapshot, trap-after-instruction, and UTC error bits.
- `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_STS`, `SQ_WAVE_IB_STS2`, `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_HW_ID1/2`, `SQ_WAVE_POPS_PACKER`, `SQ_WAVE_SCHED_MODE`, `SQ_WAVE_SHADER_CYCLES`, `SQ_WAVE_TTMP0` through `SQ_WAVE_TTMP15`, `SQ_WAVE_M0`, and `SQ_WAVE_EXEC_LO/HI` describe per-wave resource allocation, outstanding counter, identity, scratch, scheduler, timing, temporary, M0, and EXEC-mask state.

## Control Flow

This header has no software control flow. Runtime sequencing is provided by AMDGPU, KFD, firmware, or hardware microcode consumers that include the generated register headers.

The typical use pattern is:

1. A GC 11.5.0 consumer includes `gc/gc_11_5_0_offset.h` and `gc/gc_11_5_0_sh_mask.h`.
2. The consumer chooses a `reg*` or `ix*` register offset from the matching offset header.
3. It composes a `u32` with `REG_SET_FIELD`, extracts values with `REG_GET_FIELD`, or tests masks directly.
4. MMIO, SOC15, indexed-register, RLC, or wave-debug accessors perform the actual hardware reads/writes while the caller owns ordering, power-domain checks, SR-IOV ownership, and polling.

The direct GC 11.5.0 consumer visible in this tree is `drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`, which includes this header and its offset companion. That file mostly uses GCVM/GCMC fields defined in earlier chunks of the same header, but it demonstrates the integration model for this ASIC: `REG_SET_FIELD` builds register values, `RREG32_SOC15`/`WREG32_SOC15` access GC registers, and VM hub initialization derives register distances from generated offsets. The `sqind` wave fields in this chunk line up with the broader AMDGPU wave-debug pattern: other GFX generations read registers such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_STS2`, `ixSQ_WAVE_IB_DBG1`, `ixSQ_WAVE_M0`, and `ixSQ_WAVE_MODE` through `wave_read_ind()` helpers for hang/debug dumps. KFD CWSR trap handlers carry parallel hand-written constants for `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, and `SQ_WAVE_MODE` because trap save/restore code manipulates hardware wave registers directly in assembly.

The RTAVFS and CAC blocks are register metadata only here. The header does not encode when RTAVFS should be enabled, how to tune PI coefficients, how to sequence CPO/ripple-counter sampling, how to handle LUT update errors, or whether individual fields are read-only, write-one-clear, sticky, self-clearing, or firmware-owned.

## State And Persistence Behavior

The header stores no software state and persists nothing. It names fields in hardware state whose lifetime is defined by the GPU block, firmware, reset, power management, and driver programming sequence.

Represented hardware state includes:

- Pattern counter and LUT update status state. Counter fields can reflect live or latched hardware counts, while `HW_LUT_UPDATE_STATUS` fields expose completion/error/step state for table updates.
- CAC indexed state under `secacind`, including selected block/signal IDs and threshold programming.
- RTAVFS configuration state: zone windows, zone/CPO enable masks, guard bands, intercepts, PI coefficients, voltage-code anchors, VR control, low-power sensing, PSM measurement controls, AVFS enablement, per-path scaling, anchor update control, and override selectors.
- RTAVFS live/diagnostic state: CPO and ripple counts, zone-in-use bits, error code, selected ripple readback, FSM state, voltage-code readbacks, VDD regulator state, scaled CPO counts, and debug stop-at-state bits.
- SQ debug and wave state: local SQ busy flags, active/valid wave slots, wave mode/status/trap status, GPR/LDS allocation, outstanding memory/export counters, PC, hardware identity, scheduler mode, shader cycles, temporary trap registers, M0, and EXEC masks.

Persistence is hardware-defined. Some fields are configuration values that last until rewritten, reset, suspend/resume reprogramming, power-gating loss, RLC/firmware restore, or ASIC reset. Other fields are live counters/status bits that change while the GPU runs. Several controls have likely side effects when written, especially debug stop controls, save/restore CPO weights, loop-run bits, reset-retention bits, wave flush controls, and trap/status fields. The masks do not describe those side effects by themselves.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` must stay synchronized with this shift/mask header. Offsets from one ASIC generation should not be paired with masks from another.
- AMDGPU register helper infrastructure supplies `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_FIELD15_PREREG`, and related accessors.
- Indexed-register access is relevant for the `secacind`, `grtavfsind`, and `sqind` address blocks. Consumers need the correct index/data access path and instance selection, not just the bit masks.

Observed and expected integration points:

- `drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c` includes this header for GC 11.5.0 VM-hub programming and demonstrates the direct generated-header use model.
- Generic GC 11 code such as `gfx_v11_0.c`, IMU, MES, and firmware-loading paths select GC 11.5.0 firmware and register metadata for this ASIC family.
- Wave-dump and hang-diagnosis paths in AMDGPU use `SQ_WAVE_*` indexed registers across generations to capture PC, EXEC, allocation, status, and scheduler state. The GC 11.5.0 field names in this chunk are the decode contract for the same class of data on this ASIC.
- KFD CWSR and trap-handling logic depends on wave-mode/status/trap bit layouts. In assembly, those constants may be duplicated rather than included from this C header, so drift between generated headers and trap-handler constants is a meaningful integration risk.
- Power-management, firmware, or RLC/SMU-owned flows are the likely consumers for RTAVFS and fixed-pattern/LUT update registers. Even when not directly referenced in open C code, these definitions document the hardware contract for diagnostics, golden settings, debugfs tooling, or firmware-assisted programming.

## Risks And Edge Cases

- Header/offset mismatch is the largest correctness risk. These constants compile as untyped integer macros, so using GC 11.5.0 masks with another generation's offsets can silently write or decode the wrong bits.
- The chunk starts inside a register group. `FIXED_PATTERN_PERF_COUNTER_7` is incomplete here, so adjacent chunks are required for a full per-register audit.
- Full-width `RESERVED`, `UNUSED`, or `DATA` masks do not imply whole-register writes are safe. Callers still need hardware documentation or established driver sequences before changing reserved bits.
- RTAVFS fields include control, calibration, debug, counter, override, and live-status semantics in one address block. Treating all `RTAVFS_REG*` entries as ordinary configuration can accidentally start loops, force overrides, reset retention state, stop the FSM at debug points, or perturb adaptive-voltage behavior.
- Status fields such as `HW_LUT_UPDATE_STATUS`, `RTAVFS_REG121__RTAVFSERRORCODE`, `RTAVFS_REG193__RTAVFSFSMSTATE`, `SQ_DEBUG_STS_LOCAL`, `SQ_WAVE_STATUS`, and `SQ_WAVE_TRAPSTS` may be live, sticky, or clear-on-write depending on hardware semantics not captured by the mask names.
- Wave registers are highly context-sensitive. Correct reads require selecting the intended wave/SIMD/WGP/instance and ensuring the wave is halted or otherwise safely observable; otherwise PC, EXEC, counters, and trap state can race with execution.
- Trap/CWSR constants are duplicated in assembly for some generations. Any GC 11.5.0 update to `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, or `SQ_WAVE_MODE` must be checked against trap save/restore code that cannot directly consume these macros.
- Several masks span high bits or partial high words (`SQ_WAVE_HW_ID1__DP_RATE_MASK`, `SQ_WAVE_IB_STS__VS_CNT_MASK`, `RTAVFS_REG19__RTAVFSGB_ZONE4_MASK`, etc.). Callers must use unsigned 32-bit math and proper helper macros to avoid sign-extension or stale-bit bugs.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-access, and hardware-observation checks:

- Build coverage for GC 11.5.0 AMDGPU paths should catch missing or misspelled macro names when consumers use `REG_SET_FIELD`/`REG_GET_FIELD`.
- A generated-header consistency check should verify that every complete register field in the range has both `__SHIFT` and `_MASK` definitions, allowing for known chunk-boundary exceptions such as `FIXED_PATTERN_PERF_COUNTER_7`.
- ASIC bring-up or VM-hub smoke tests on GC 11.5.0 hardware should confirm that including this header alongside `gc_11_5_0_offset.h` still allows GART enable/disable, VM fault handling, and reset/resume flows to complete.
- Wave dump or GPU hang diagnostics should produce plausible `SQ_WAVE_*` values: valid PC high/low pairs, EXEC masks, wave IDs, SIMD/WGP/SA/SE IDs, allocation sizes, and outstanding counter fields.
- Trap/CWSR tests should verify that saved/restored wave status, trap status, mode, TTMP, M0, and EXEC state match the hardware layout for the active ASIC.
- Power-management or firmware diagnostics for RTAVFS should check that zone enable masks, CPO start/stop windows, ripple counts, FSM state, error code, voltage-code readbacks, and override selectors decode to expected values after firmware or RLC programming.
- Negative testing should avoid blind writes to `RESERVED`/`UNUSED` fields and should verify that read-modify-write paths preserve undocumented bits unless an approved golden-register table intentionally writes a full register value.
