# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_sh_mask.h lines 2570-2956

## Scope

This chunk is the tail of the generated AMD SDMA1 4.2.2 shift/mask header. It contains C preprocessor constants only: `__SHIFT` bit positions and `_MASK` field masks for SDMA1 RLC queue registers. The range starts with the final field definitions for `SDMA1_RLC5_MIDCMD_CNTL`, then covers complete repeated register-field blocks for `SDMA1_RLC6_*` and `SDMA1_RLC7_*`, and ends with the file's closing `#endif`.

The file has no functions, structs, storage, locking, callbacks, or direct MMIO access. Its purpose is to describe the bit geometry of hardware registers; companion offset headers provide register addresses, and AMDGPU/KFD code performs the reads and writes.

## Purpose and Register Families

The macros describe the SDMA1 engine's RLC queue slots 6 and 7 on ASICs using the 4.2.2 SDMA register layout, plus the end of queue slot 5 mid-command state. Each RLC queue block exposes the same families of fields:

- Ring-buffer control: `RB_ENABLE`, `RB_SIZE`, ring swap flags, read-pointer writeback enable/swap/timer, privileged mode, and `RB_VMID`.
- Ring-buffer base and pointers: low/high base address fields, read pointer, write pointer, and read-pointer writeback address fields.
- Write-pointer polling: polling enable, swap, F32 polling enable, frequency, idle poll count, and polling address low/high fields.
- Indirect buffer state: IB enable/swap, switch-inside-IB, command VMID, IB read pointer, offset, base low/high, size, and remaining sub-IB size.
- Queue status and control: skip count, context status bits, doorbell enable/captured status, write-pointer update status, doorbell log, watermark limits, doorbell offset, context-save area address, preempt request, dummy register, AQL control, minor pointer update, and mid-command data/control registers.

The repeated `RLC6` and `RLC7` macro names identify two independent queue contexts in the SDMA1 engine. The layout matches nearby `RLC0`-`RLC5` blocks and equivalent SDMA0/SDMA2-SDMA7 generated headers, allowing generic queue code to compute an RLC register offset from queue id.

## Important APIs, Types, and Macros

This header's public interface is the AMD register-field macro convention:

- `SDMA1_RLC<n>_<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit number for a field.
- `SDMA1_RLC<n>_<REGISTER>__<FIELD>_MASK` gives the already-shifted 32-bit field mask.
- The corresponding register addresses are in `sdma1_4_2_2_offset.h` as `mmSDMA1_RLC6_*` and `mmSDMA1_RLC7_*`.

The notable fields in this chunk include `RB_ENABLE`, `RB_SIZE`, `RB_VMID`, `RPTR_WRITEBACK_*`, `DOORBELL__ENABLE`, `DOORBELL_OFFSET__OFFSET`, `CONTEXT_STATUS__IDLE`, `PREEMPT__IB_PREEMPT`, `RB_AQL_CNTL__AQL_ENABLE`, and `MIDCMD_CNTL` fields for valid mid-command data, copy mode, split state, and preemption allowance.

The direct in-tree consumer of this exact header is `amdgpu_amdkfd_arcturus.c`, which includes all `sdma0` through `sdma7` 4.2.2 offset and shift/mask headers. The Arcturus KFD path uses `struct v9_sdma_mqd` queue descriptors and generic RLC0-relative register programming: `get_sdma_rlc_reg_offset()` selects the SDMA engine base from `mmSDMA1_RLC0_RB_CNTL` for engine 1, then adds `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`. Therefore these `RLC6` and `RLC7` register definitions correspond to queue ids 6 and 7 even when the code uses RLC0 field names for common layout operations.

## Control Flow and Data Flow

There is no executable control flow in the header. Runtime use is indirect:

1. KFD/AMDGPU builds an MQD for an SDMA queue, including ring buffer base, size, VMID, read/write pointers, doorbell offset, and writeback addresses.
2. `kgd_arcturus_hqd_sdma_load()` computes the engine/queue register offset, disables the queue by clearing `RB_ENABLE`, waits until `CONTEXT_STATUS__IDLE` is set, writes doorbell and pointer registers, toggles `MINOR_PTR_UPDATE` while synchronizing the write pointer, writes base and read-pointer writeback addresses, then sets `RB_ENABLE`.
3. `kgd_arcturus_hqd_sdma_dump()` walks the RLC register windows, including the mid-command data/control range described by this chunk, for diagnostics.
4. `kgd_arcturus_hqd_sdma_is_occupied()` reads the queue's `RB_CNTL` and tests `RB_ENABLE`.
5. `kgd_arcturus_hqd_sdma_destroy()` clears `RB_ENABLE`, waits for `CONTEXT_STATUS__IDLE`, clears the doorbell register, re-enables the ring control register, and saves read-pointer state back into the MQD.

For queue ids 6 and 7 on SDMA1, the same flow lands on the `mmSDMA1_RLC6_*` or `mmSDMA1_RLC7_*` address blocks. Field layout consistency is what makes the RLC0-relative implementation valid.

## State and Persistence

The header itself has only compile-time constants and no persistent software state.

The hardware registers described by the masks hold live queue state:

- Ring-buffer base, size, VMID, privilege, and enable bits define whether the queue can fetch packets and under which VM context.
- Read/write pointers and pointer writeback address fields synchronize software, hardware, and memory-visible queue progress.
- Doorbell offset and doorbell enable/captured bits connect CPU/KFD queue signaling to the hardware queue.
- `CONTEXT_STATUS` bits expose selected, idle, expired, exception, context-switch, preempted, and preempt-disable states used by load/destroy/reset flows.
- IB and mid-command registers describe in-flight indirect-buffer execution and partial command state that may need to be dumped or restored across preemption/debug paths.
- CSA address fields identify context-save storage for queue state.
- AQL fields configure HSA-style packet processing for queues that use AQL semantics.

Persistence across reset, suspend/resume, queue teardown, and process eviction is controlled by AMDGPU/KFD and hardware firmware. This header only defines how software should address individual fields.

## Dependencies and Integration Points

This chunk depends on the generated AMD register database:

- `sdma1_4_2_2_offset.h` provides the matching `mmSDMA1_RLC6_*` and `mmSDMA1_RLC7_*` register offsets.
- Other generated `sdmaN_4_2_2_sh_mask.h` files mirror the same queue layout for sibling SDMA engines.
- AMDGPU register helpers such as `REG_SET_FIELD`, `RREG32`, `WREG32`, and `SOC15_REG_OFFSET` consume the generated constants indirectly through KFD and SDMA engine code.
- `amdgpu_amdkfd_arcturus.c` integrates this register layout with KFD MQD load, dump, occupancy, and destroy operations for Arcturus-class devices.
- `v9_sdma_mqd` is the software persistence format that stores the register images later written into the RLC queue windows.

The chunk closes the header guard, so merge/reconciliation should treat it as the final segment for the file.

## Risks and Edge Cases

- The chunk begins in the middle of the `RLC5_MIDCMD_CNTL` block. The final file-level research should reconcile those first RLC5 lines with the preceding chunk.
- Repeated `RLC6` and `RLC7` blocks are copy/generator sensitive. A wrong prefix, shift, or mask could affect only high-numbered SDMA queues and escape lower-queue testing.
- The RLC0-relative programming path assumes every queue block has identical spacing and compatible field layout. Divergence in `RLC6` or `RLC7` would break queue ids 6 and 7 even if direct macro references are rare.
- Address fields have alignment masks: doorbell offset and CSA/RPTR/poll low addresses use low-bit-zero masks, while IB base low starts at bit 5. Callers must not treat these as arbitrary full-width values.
- Full-width pointer and mid-command data masks use `0xFFFFFFFFL`; code should avoid signed arithmetic assumptions and preserve high/low word ordering.
- Queue enable/disable and idle polling are synchronization-sensitive. Incorrect `RB_ENABLE` or `CONTEXT_STATUS__IDLE` masks can cause timeout, queue corruption, or teardown while hardware is still active.
- Doorbell enable/captured and doorbell log fields are externally visible signaling state. Bad masks can make a queue miss submissions or report misleading backend errors.
- Preemption and mid-command state fields are relevant to context switching and diagnostics. Wrong `MIDCMD_CNTL` masks can misinterpret partially executed command state.

## Test and Validation Signals

Useful validation signals are mostly compile-time plus hardware/KFD integration:

- Build AMDGPU with Arcturus/KFD support so the 4.2.2 SDMA1 offset and shift/mask headers are included and macro names are validated.
- Compare this chunk with `sdma1_4_2_2_offset.h` to confirm every RLC6/RLC7 address has matching field definitions and expected register spacing.
- Run KFD SDMA queue creation and destruction with SDMA1 queue ids 6 and 7, checking that load waits for idle, programs doorbells and pointers, enables the ring, and teardown returns to idle without `-ETIME`.
- Use queue dump paths to verify RLC6/RLC7 register windows include RB, status, CSA, preempt, AQL, minor pointer update, and mid-command registers in the expected order.
- Exercise user write-pointer updates, read-pointer writeback, doorbell submission, and AQL packet queues to catch alignment or mask errors.
- Test preemption, process eviction, GPU reset, and suspend/resume scenarios so context status, CSA, IB, and mid-command fields are observed under non-idle conditions.
- Cross-check against sibling SDMA engine 4.2.2 headers and older `sdma1_4_2` layouts for unintended generator drift, while treating the ASIC register specification as authoritative.
