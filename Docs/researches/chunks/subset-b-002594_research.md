# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 4997-7586

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the middle of `SDMA1_SDMA_QUEUE0_RB_CNTL`, immediately after the queue-0 `RB_ENABLE` mask, and continue through the rest of SDMA1 queue 0 plus complete replicated SDMA1 queue definitions for queues 1 through 9. The chunk then enters `CHIP_XCD_gfxip_xcc_gfx_cpwd_sdma_sdmahypdec:1`, defining SDMA1 virtualization/context register fields, context/public register classification bitmaps, and ending in the `SDMA1_SDMA_PUB_REG_TYPE1` shift-only portion at `SDMA_DCC_CNTL`.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for GC 12.1.0 registers. Driver code pairs these macros with register addresses from the matching `gc_12_1_0_offset.h` header and uses field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to avoid open-coded bit positions.

This chunk is centered on SDMA1 queue and virtualization metadata:

- SDMA1 queue ring buffer control fields for ring enable, ring size, write-pointer polling, byte swapping, MCU write-pointer polling, read-pointer writeback, privilege, and VMID assignment.
- Queue base, read pointer, write pointer, read-pointer writeback address, indirect-buffer control/base/size, doorbell, context-save-area address, scheduling, preemption, write-pointer polling, AQL, context switch, mid-command, utilization, MQD, and context status fields.
- Replicated queue field groups for queues 0 through 9. Queue 0 starts partially in this chunk; queues 1 through 9 are complete within the range.
- SDMA1 hypervisor/context fields for VM context address, active virtual function identity, VM context privilege/VMID/memory type, and virtual reset requests.
- Register type bitmap fields that classify which SDMA queue/public registers belong to context or public register save/restore groups.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion offset header as `regSDMA1_*` macros.
- AMDGPU consumers use these through field packing/extraction helpers, MMIO accessors, indexed register access, queue MQD programming, suspend/resume save-restore logic, debug dumps, reset paths, and virtualization code.

The main macro families in this slice are:

- `SDMA1_SDMA_QUEUE{0..9}_RB_CNTL`: queue ring setup. Fields include `RB_ENABLE`, `RB_SIZE`, `WPTR_POLL_ENABLE`, `RB_SWAP_ENABLE`, `WPTR_POLL_SWAP_ENABLE`, `MCU_WPTR_POLL_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_SWAP_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, and `RB_VMID`. For queue 0, this chunk includes masks but the first shifts are in the previous chunk.
- `SDMA1_SDMA_QUEUE{0..9}_RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI`: low/high ring base and pointer fields. Most are full 32-bit data or offset fields.
- `SDMA1_SDMA_QUEUE{0..9}_RB_RPTR_ADDR_LO/HI` and `RB_WPTR_POLL_ADDR_LO/HI`: memory addresses used for read-pointer writeback and write-pointer polling. Low parts use an address shift of 2 with `0xFFFFFFFC` alignment masks.
- `SDMA1_SDMA_QUEUE{0..9}_IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, and `IB_SIZE`: indirect-buffer enable, byte swapping, inside-IB switching, command VMID, privilege, pointer, base, and size fields.
- `SDMA1_SDMA_QUEUE{0..9}_DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`: doorbell enable/capture, logged doorbell data/error, and offset fields.
- `SDMA1_SDMA_QUEUE{0..9}_CSA_ADDR_LO/HI`: context-save-area address fields.
- `SDMA1_SDMA_QUEUE{0..9}_SCHEDULE_CNTL`: global, process, local, and context-quantum scheduling selectors.
- `SDMA1_SDMA_QUEUE{0..9}_IB_SUB_REMAIN`, `PREEMPT`, `DUMMY_REG`, and `MINOR_PTR_UPDATE`: remaining IB sub-size, IB preemption, scratch/dummy data, and minor pointer update enable.
- `SDMA1_SDMA_QUEUE{0..9}_RB_AQL_CNTL`: AQL mode, packet size, packet step, mid-command preempt, data restore, and overlap enable fields.
- `SDMA1_SDMA_QUEUE{0..9}_CONTEXT_SWITCH_STATUS`: queue exception/status bits for RB preempt, VM hole, page fault, command timeout, queue hang, doorbell error, SRAM ECC, DRAM ECC, and write-pointer less than read-pointer conditions.
- `SDMA1_SDMA_QUEUE{0..9}_MIDCMD_CNTL` and `MIDCMD_DATA0..10`: mid-command preemption state and captured command data.
- `SDMA1_SDMA_QUEUE{0..9}_UTILIZATION_LO/HI`, `WAIT_UNSATISFIED_THD`, `MQD_BASE_ADDR_LO/HI`, `MQD_CONTROL`, and `CONTEXT_STATUS`: utilization counters, wait threshold, MQD address/control, and selected/use-IB/idle/expired/valid/error/exception/wait-for-idle/ready state.
- `SDMA1_SDMA_VM_CTX_LO/HI`, `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, and `VIRT_RESET_REQ`: hypervisor/virtualization context address, VF/PF identification, VMID and memory attributes, busy reporting, and reset request masks.
- `SDMA1_SDMA_CONTEXT_REG_TYPE0/1/2`: bitmap classification for context state. Type 0 covers queue-0 ring, IB, doorbell, scheduling, preempt, AQL, context switch, and mid-command control registers; type 1 covers mid-command data, utilization, MQD, context status, dummy registers, and reserved bits; type 2 is fully reserved in this chunk.
- `SDMA1_SDMA_PUB_REG_TYPE0` and partial `SDMA1_SDMA_PUB_REG_TYPE1`: bitmap classification for public SDMA registers such as decoder start, MCU control, ucode revision, timestamps, power/control/cache/chicken bits, read-pointer fetch, program/status/control/freezing/quantum/watchdog/queue-status/atomic/DCC registers.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 12.1.0 register headers for the active ASIC generation.
2. Use a queue and SDMA instance to select the matching `regSDMA1_SDMA_QUEUE*_...` address from `gc_12_1_0_offset.h`.
3. Read, construct, or update a 32-bit register value using the `__SHIFT` and `__MASK` pairs.
4. Program or decode queue ring state, IB state, doorbells, MQD pointers, context-save addresses, AQL/mid-command preemption state, context-switch status, or virtualization metadata.
5. Feed decoded state into queue bring-up, KFD/HQD dumping, suspend/resume, reset/recovery, SR-IOV virtualization, diagnostics, and performance/status reporting.

One direct integration point in this tree is `amdgpu_amdkfd_gfx_v12_1.c`, where `get_sdma_rlc_reg_offset()` uses `regSDMA1_SDMA_QUEUE0_RB_CNTL` as the base for SDMA1 queue register offset calculations and derives per-queue spacing from the queue-0 to queue-1 register address delta. The masks in this chunk describe the fields of those addressed queue registers after the address has been selected.

For queue programming, driver code typically disables or initializes the ring, writes base and pointer addresses, configures read-pointer writeback and optional write-pointer polling, sets doorbell offset/enable, configures IB/AQL behavior, writes MQD base/control state, and finally enables scheduling/ring execution. For diagnostics and recovery, code reads context status, context switch status, utilization, pointer, doorbell log, and mid-command data fields to determine whether the queue is idle, hung, faulted, preempted, or waiting on memory/doorbell state.

For virtualization/context management, hypervisor-aware paths use the VM context address/control, active function, and virtual reset fields to identify VF/PF ownership and manage SDMA context state. The context/public register type bitmaps are not queue controls themselves; they classify registers for save/restore, isolation, or virtualization handling.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

Queue ring, IB, doorbell, MQD, context-save, AQL, scheduling, and VMID fields are persistent queue state until the driver reprograms them, a context switch replaces them, or hardware reset clears them. Bad packing of low/high base addresses, pointer offsets, VMID, privilege, or doorbell offsets can make SDMA fetch commands from the wrong memory, write back pointers to the wrong location, signal the wrong queue, or execute work under the wrong memory context.

Context status, context switch status, utilization, doorbell log, and mid-command fields are live diagnostic or hardware-updated state. Some status bits may be sticky, latched, write-one-to-clear, or volatile according to hardware rules that are not encoded in this header. The masks only define bit positions.

`SDMA1_SDMA_VM_CTX_*`, `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, and `VIRT_RESET_REQ` describe virtualization state that affects PF/VF isolation, VMID selection, memory physical/type behavior, busy reporting, and reset routing. Incorrect writes can affect more than one queue because these are SDMA1 hypervisor/context registers rather than per-queue ring fields.

`SDMA1_SDMA_CONTEXT_REG_TYPE*` and `SDMA1_SDMA_PUB_REG_TYPE*` are bitmap descriptors used to classify register groups. Their state can affect save/restore or virtualization logic if programmed or interpreted by firmware/driver flows; reserved bits must be preserved or ignored according to the hardware contract.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h` provides matching `regSDMA1_*` addresses. Queue 0 starts at `regSDMA1_SDMA_QUEUE0_RB_CNTL`, queue 1 starts at `regSDMA1_SDMA_QUEUE1_RB_CNTL`, and the hypervisor/context registers in this chunk are at the `0x58b*` offset range with base index 1.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12_1.c` uses SDMA0/SDMA1 queue register bases and per-queue spacing to dump or access SDMA HQD/RLC queue state for KFD.
- AMDGPU register helper macros and MMIO/indexed-register accessors provide the runtime mechanism for setting and extracting these fields.
- SDMA, KFD compute scheduling, HQD/MQD setup, doorbell management, queue preemption, reset/recovery, suspend/resume, SR-IOV virtualization, diagnostics, and performance/status paths rely on these bit assignments.

Integration points include queue ring allocation and enablement, read/write pointer handling, read-pointer writeback buffers, doorbell offset allocation, IB dispatch, AQL queues, mid-command preemption and restore, utilization accounting, queue context switching, MQD placement, VMID assignment, VF/PF attribution, virtual reset routing, and register save/restore classification.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading queue status.
- The chunk begins mid-register. The `SDMA1_SDMA_QUEUE0_RB_CNTL__RB_ENABLE` shift and mask are in the previous chunk, so final per-file reconciliation must merge adjacent chunks for complete queue-0 `RB_CNTL` coverage.
- The chunk ends mid-register family. `SDMA1_SDMA_PUB_REG_TYPE1` masks and later public register type fields continue after line 7586.
- Queue groups are repetitive but offset-sensitive. Assuming queue symmetry without using the generated offsets can target the wrong queue, especially when code computes per-queue spacing.
- Low address fields often require 4-byte alignment via `ADDR__SHIFT 0x2` and `0xFFFFFFFC` style masks. Packing raw byte addresses incorrectly can drop low bits or program an invalid address.
- `RB_VMID`, `CMD_VMID`, `MQD_CONTROL__VMID`, `RB_PRIV`, and `IB_PRIV` affect memory context and privilege. Incorrect values can cause VM faults, isolation failures, or work execution under the wrong address space.
- Doorbell fields have both enable/captured status and offset/log fields. Confusing offset units or stale captured/log bits can produce missed queue submissions or misleading fault attribution.
- Context switch status contains exception bits for VM hole, page fault, timeout, hang, doorbell error, ECC, and pointer ordering. These bits may need hardware-specific clearing and should not be treated as passive read-only metadata without checking the programming guide.
- Mid-command preemption fields and `MIDCMD_DATA0..10` capture in-flight command state. Writing or restoring them with stale data can corrupt resumed SDMA work.
- AQL and overlap/mid-command restore controls change queue execution semantics. Incorrect enablement can break compute queues that expect packetized AQL behavior or preemption restore support.
- Hypervisor fields are broader than one queue. `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, and `VIRT_RESET_REQ` mistakes can affect PF/VF isolation and reset behavior.
- `CONTEXT_REG_TYPE*` and `PUB_REG_TYPE*` contain reserved fields. Full-register writes must preserve reserved bits unless a hardware-defined sequence says otherwise.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_1_0_sh_mask.h`, especially GC 12.1.0 SDMA, KFD, queue, doorbell, reset, virtualization, and diagnostics paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 4997-7586.
- Cross-check that every register in this chunk has a matching `regSDMA1_*` address in `gc_12_1_0_offset.h`, and that queue-to-queue spacing remains consistent for queues 0 through 9.
- Static mask/shift sanity checks: masks should align with shifts, full-width fields should use `0xFFFFFFFFL`, aligned address fields should keep low-bit masks clear, and replicated queue families should remain structurally identical where intended.
- SDMA queue bring-up tests that program ring base, size, read/write pointers, read-pointer writeback, write-pointer polling, doorbells, IB controls, AQL controls, MQD base/control, and scheduling fields, then submit known copy/fill workloads.
- KFD/HQD dump tests that verify `amdgpu_amdkfd_gfx_v12_1.c` reads the expected SDMA1 queue registers and decodes queue state consistently across queue IDs.
- Fault-injection or recovery tests that exercise VM hole, page fault, command timeout, queue hang, doorbell error, ECC, write-pointer less-than-read-pointer, preemption, and context-status decode.
- Doorbell tests that validate offset programming, enable/capture behavior, logged data, and queue wakeup across SDMA1 queues.
- Preemption and context-switch tests that validate `IB_PREEMPT`, mid-command data capture/restore, `CONTEXT_STATUS`, and `CONTEXT_SWITCH_STATUS` transitions.
- Virtualization/SR-IOV tests that validate active VF/PF identification, VM context address/control, busy reporting, and virtual reset request behavior without cross-function leakage.
- Suspend/resume or GPU reset tests that verify context/public register type bitmaps select the right SDMA queue/public state for save/restore.
- Runtime warning signals include SDMA queues that fail to start, stale read/write pointers, doorbells that do not wake queues, repeated VM faults, incorrect VMID attribution, stuck preemption, false hang reports, corrupted resumed work after mid-command restore, or VF/PF reset leakage.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002594`. It covers lines 4997-7586 of `gc_12_1_0_sh_mask.h`. The final per-file research should merge this with the previous chunk for the start of `SDMA1_SDMA_QUEUE0_RB_CNTL` and with the next chunk for the remainder of `SDMA1_SDMA_PUB_REG_TYPE1` and later SDMA1 public/VM fields.
