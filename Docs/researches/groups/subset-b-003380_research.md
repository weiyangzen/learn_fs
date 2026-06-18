# Research group subset-b-003380

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_default.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_default.h

### Purpose

`sdma1_4_0_default.h` is a generated AMDGPU register default-value header for the SDMA1 engine in the SDMA 4.0 register block. It does not implement executable logic; it publishes reset or expected default 32-bit values as `#define` constants named `mmSDMA1_*_DEFAULT`. Driver code and diagnostic code can use these constants together with the matching offset and shift/mask headers to initialize, compare, dump, or document SDMA1 hardware state.

The file covers the `sdma1_sdma1dec` address block and defines 255 register defaults: 86 core SDMA1 defaults, 43 GFX queue defaults, 42 PAGE queue defaults, and 84 RLC queue defaults for RLC0 and RLC1. The family mirrors `sdma1_4_0_offset.h`, so each default macro is meaningful only when paired with the matching SDMA 4.0 register address map.

### Important APIs, types, and functions

There are no C types or functions. The public API is the preprocessor surface:

- Include guard `_sdma1_4_0_DEFAULT_HEADER`.
- One macro per defaulted register, for example `mmSDMA1_CNTL_DEFAULT`, `mmSDMA1_STATUS_REG_DEFAULT`, `mmSDMA1_UTCL1_CNTL_DEFAULT`, `mmSDMA1_GFX_RB_CNTL_DEFAULT`, `mmSDMA1_PAGE_RB_CNTL_DEFAULT`, `mmSDMA1_RLC0_RB_CNTL_DEFAULT`, and `mmSDMA1_RLC1_RB_CNTL_DEFAULT`.
- Register classification defaults such as `mmSDMA1_CONTEXT_REG_TYPE0_DEFAULT` through `TYPE3` and `mmSDMA1_PUB_REG_TYPE0_DEFAULT` through `TYPE3`, which encode hardware-visible register grouping bitmaps.

The constants are raw literal values. Callers are expected to use the companion `sdma1_4_0_sh_mask.h` field definitions if they need to interpret or modify individual bits.

### Control flow

The header has no runtime control flow. Its compile-time flow is linear: copyright/license, include guard, generated macro list, and closing `#endif`. Runtime behavior emerges only in consumers that select a register offset, read or write the hardware register, and compare or compose values with these defaults.

### State and persistence behavior

The header itself owns no mutable state and persists nothing. It describes hardware reset/default state for SDMA1 registers. Several defaults are operationally important because they seed expected state for persistent GPU engine programming:

- Queue ring controls such as `GFX_RB_CNTL`, `PAGE_RB_CNTL`, `RLC0_RB_CNTL`, and `RLC1_RB_CNTL` default to `0x00040000`, matching the `RPTR_WRITEBACK_TIMER` field placement in the shift/mask header.
- Most base addresses, read/write pointers, indirect buffer registers, CSA addresses, and doorbell offsets default to zero, which is the expected unprogrammed state before queue setup.
- `mmSDMA1_CNTL_DEFAULT` is `0x00000002`, meaning the default is not an all-zero control register.
- Status and configuration defaults such as `STATUS_REG`, `STATUS1_REG`, `UTCL1_*`, `BA_THRESHOLD`, `RELAX_ORDERING_LUT`, `PERFMON_CNTL`, and `CRD_CNTL` document non-zero hardware reset state that debug tooling should not treat as driver-written state.

### Dependencies

This file depends only on the C preprocessor. Semantically, it depends on the generated SDMA 4.0 SDMA1 register model:

- `sdma1_4_0_offset.h` supplies the matching register offsets.
- `sdma1_4_0_sh_mask.h` supplies bit positions and masks for interpreting values.
- Sibling SDMA0 headers must remain consistent where driver code derives SDMA1 addresses from SDMA0 address arithmetic.

### Integration points

The directly observed AMDGPU include users in this tree are mostly offset and mask consumers, but this default header belongs to the same generated hardware interface set used by SOC15/GFX9 SDMA setup. `soc15.c` includes `sdma1_4_0_offset.h`, and `amdgpu_amdkfd_gfx_v9.c` includes the SDMA1 4.0 offset and shift/mask headers for KFD SDMA queue programming. The defaults are suitable for register dump baselines, reset validation, and bring-up comparisons in the same SDMA1 block.

### Risks

- The defaults must not be mixed with a different SDMA generation. SDMA 4.2.2 moves some queue windows and expands RLC queues, so an apparently valid `mmSDMA1_*_DEFAULT` name can describe the wrong hardware if paired with the wrong offset header.
- Non-zero defaults can be misread as driver configuration. Test and debug code should distinguish reset state from values programmed during ring setup.
- Register classification defaults (`CONTEXT_REG_TYPE*`, `PUB_REG_TYPE*`) are compact bitmaps. A stale bitmap can break save/restore, virtualization exposure, or register-access policy even though no C compiler error appears.
- Because these are generated constants, local manual edits are high risk. The source of truth is normally an ASIC register database, not handwritten kernel code.

### Test signals

Useful validation signals are compile-time and hardware-facing:

- Kernel build of AMDGPU/KFD translation units that include the matching SDMA1 4.0 headers.
- Static comparison that every `mmSDMA1_*_DEFAULT` has a matching `mmSDMA1_*` offset in `sdma1_4_0_offset.h`.
- Register dump checks on GFX9/SOC15 hardware after reset or resume, especially non-zero defaults in `CNTL`, `CLK_CTRL`, `STATUS*`, `UTCL1_*`, `RB_CNTL`, and `PERFMON_CNTL`.
- KFD SDMA queue creation and teardown tests for GFX, PAGE, RLC0, and RLC1 paths, verifying that ring pointers and doorbells start from clean defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_default.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_offset.h

### Purpose

`sdma1_4_0_offset.h` is the generated SDMA1 register offset map for SDMA 4.0. It maps symbolic register names to word offsets inside the `sdma1_sdma1dec` address block with base address `0x5180`. AMDGPU uses this kind of header with SOC15 register macros to compute MMIO addresses for SDMA1 engine programming.

The file defines 255 real register offsets plus a `_BASE_IDX` macro for each register. The register families are 86 core SDMA registers, 43 GFX queue registers, 42 PAGE queue registers, and 84 RLC queue registers covering RLC0 and RLC1. All `_BASE_IDX` values are `0`, so this header describes one base-index space.

### Important APIs, types, and functions

There are no functions or data structures. The exported API is a set of preprocessor constants:

- Include guard `_sdma1_4_0_OFFSET_HEADER`.
- `mmSDMA1_*` offset macros such as `mmSDMA1_UCODE_ADDR`, `mmSDMA1_VM_CNTL`, `mmSDMA1_CNTL`, `mmSDMA1_STATUS_REG`, `mmSDMA1_UTCL1_CNTL`, and `mmSDMA1_GPU_IOV_VIOLATION_LOG`.
- Queue windows starting at `mmSDMA1_GFX_RB_CNTL` (`0x0080`), `mmSDMA1_PAGE_RB_CNTL` (`0x00e0`), `mmSDMA1_RLC0_RB_CNTL` (`0x0140`), and `mmSDMA1_RLC1_RB_CNTL` (`0x01a0`).
- Matching `*_BASE_IDX` macros, all set to `0`, used by generated register access helpers.

The offsets are register-index values, not byte addresses. Consumers normally pass them through `SOC15_REG_OFFSET(...)` or related AMDGPU register access macros.

### Control flow

The header has no runtime control flow. It supplies constants to consumers. A representative consumer pattern appears in `amdgpu_amdkfd_gfx_v9.c`, where KFD computes an SDMA RLC queue register base from an engine base plus `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`. In that flow, this header is part of the address arithmetic for SDMA1 engine 1.

### State and persistence behavior

The file stores no mutable state. It defines the persistent contract between driver source and hardware register layout. The most stateful hardware areas represented are:

- Microcode access registers (`UCODE_ADDR`, `UCODE_DATA`, `UCODE_CHECKSUM`).
- VM and virtualization registers (`VM_CNTL`, `VM_CTX_*`, `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `VF_ENABLE`, `MMHUB_TRUSTLVL`, `GPU_IOV_VIOLATION_LOG`).
- Ring and indirect-buffer state for GFX, PAGE, RLC0, and RLC1 queues, including base addresses, read/write pointers, poll addresses, doorbells, context status, CSA addresses, preemption, AQL control, and mid-command capture data.
- Diagnostics and performance state (`STATUS*`, EDC counters, error logs, perf counters).

Persistence is entirely in hardware registers and in driver memory programmed through those registers. Changing an offset changes where that state is read or written.

### Dependencies

This header depends on:

- The SOC15 register access layer that combines block, instance, base index, and offset into final MMIO addresses.
- Matching SDMA0 offset headers where arithmetic uses SDMA0 deltas to address SDMA1 queues.
- `sdma1_4_0_sh_mask.h` for bitfield interpretation and `sdma1_4_0_default.h` for expected default values.

Observed include points include `amdgpu_amdkfd_gfx_v9.c` and `soc15.c`.

### Integration points

The key integration surface is KFD and SOC15 SDMA programming. `amdgpu_amdkfd_gfx_v9.c` includes this header and computes SDMA RLC register offsets for queue programming. `soc15.c` includes the SDMA1 4.0 offset map alongside SDMA0, GC, NBIO, MP, UVD, GFXHUB, and MMHUB register maps for SOC15 initialization and access routing.

The register names also line up with the SDMA1 4.0 shift/mask and default headers, so generated code, debugfs dumps, trace helpers, and reset code can use a consistent name across address, field, and default-value layers.

### Risks

- Offset headers are hardware contracts. A single wrong numeric offset can redirect a register write to an unrelated register and cause hangs, queue corruption, VM faults, or failed preemption.
- SDMA1 4.0 has only RLC0 and RLC1 in this header. Code that assumes more RLC queues must use a newer SDMA map such as 4.2.2.
- Queue spacing is part of driver arithmetic. In this file `RLC1_RB_CNTL - RLC0_RB_CNTL` is `0x60`; consumers that derive queue windows depend on that spacing remaining correct.
- Do not substitute `sdma1_4_2_2_offset.h` for this header. The base address and queue offsets differ, including PAGE and RLC window starts.

### Test signals

- Build coverage for `amdgpu_amdkfd_gfx_v9.c` and `soc15.c`.
- Static checks that every offset has a `_BASE_IDX`, every default macro in `sdma1_4_0_default.h` has a matching offset, and every commented register block in `sdma1_4_0_sh_mask.h` has a matching offset.
- Runtime KFD SDMA queue tests that exercise engine 1 and queue IDs 0 and 1.
- Suspend/resume and GPU reset tests that reprogram SDMA1 rings, poll read/write pointers, and verify doorbell behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_sh_mask.h

### Purpose

`sdma1_4_0_sh_mask.h` is the generated bitfield definition header for the SDMA1 SDMA 4.0 register block. It maps each register field to a `__SHIFT` value and a mask literal so AMDGPU code can compose, update, and decode SDMA1 register values without hard-coded bit numbers.

The file describes 255 register comment blocks and exports 1,528 field macros: 764 shift macros and 764 mask macros. It covers core SDMA1 registers plus the GFX, PAGE, RLC0, and RLC1 queue windows represented in `sdma1_4_0_offset.h`.

### Important APIs, types, and functions

There are no C functions or types. The public API is preprocessor field metadata:

- Include guard `_sdma1_4_0_SH_MASK_HEADER`.
- Field shift macros named `SDMA1_REGISTER__FIELD__SHIFT`.
- Field mask macros named `SDMA1_REGISTER__FIELD_MASK`.

Important field groups include:

- VM and virtualization: `SDMA1_VM_CNTL__CMD`, `SDMA1_ACTIVE_FCN_ID__VFID/VF`, `SDMA1_VM_CTX_CNTL__PRIV/VMID`, `SDMA1_VIRT_RESET_REQ__VF/PF`, `SDMA1_VF_ENABLE__VF_ENABLE`, `SDMA1_GPU_IOV_VIOLATION_LOG__*`, and `SDMA1_MMHUB_TRUSTLVL__SECFLAG*`.
- Control and power: `SDMA1_CNTL__TRAP_ENABLE`, `UTC_L1_ENABLE`, preemption and context-switch fields, `SDMA1_POWER_CNTL__*`, `SDMA1_CLK_CTRL__*`, `SDMA1_CHICKEN_BITS__*`, and `SDMA1_RELAX_ORDERING_LUT__*`.
- Diagnostics: `SDMA1_STATUS_REG__*`, `SDMA1_STATUS1_REG__*`, `SDMA1_STATUS2_REG__*`, `SDMA1_STATUS3_REG__*`, EDC counters, error log fields, and perf counter fields.
- Ring/IB programming: repeated field layouts for `GFX`, `PAGE`, `RLC0`, and `RLC1` queue windows, including ring enable/size, pointer writeback, VMID, IB enable/base/size, doorbell enable/captured, context status, preemption, AQL, and mid-command fields.

### Control flow

The header has no direct control flow. It participates in caller-side read-modify-write and decode flows:

1. A consumer selects a register offset from `sdma1_4_0_offset.h`.
2. It builds a value with this header's masks and shifts, or decodes a read value with the same field definitions.
3. It writes the composed value through AMDGPU register access helpers or interprets the result for status, fault, or queue state.

The repeated queue field groups allow the same logical programming flow to be applied to GFX, PAGE, RLC0, and RLC1 by swapping register prefixes.

### State and persistence behavior

This file owns no state. It defines how hardware register state is partitioned into fields. The state described includes:

- Queue residency and scheduling state through `*_CONTEXT_STATUS`, `*_PREEMPT`, `*_MIDCMD_*`, and context save area address fields.
- Ring persistence through `*_RB_BASE*`, `*_RB_RPTR*`, `*_RB_WPTR*`, and writeback/poll address fields.
- VM and memory transaction state through UTCL1 watermarks, invalidation registers, XNACK capture registers, physical address decode fields, and relaxed-ordering controls.
- Error and observability state through EDC, error log, GPU IOV violation log, status, and perf counter fields.

Because field masks define valid writable bits, stale masks can cause state loss during read-modify-write operations or expose reserved bits to writes.

### Dependencies

The header depends on the matching SDMA1 4.0 register names and offsets from `sdma1_4_0_offset.h`. It is included directly by `amdgpu_amdkfd_gfx_v9.c`, where KFD uses SDMA register field definitions for GFX9 SDMA queue handling. It also aligns with `sdma1_4_0_default.h`, which provides reset values that can be decoded with these masks.

The macros are raw C preprocessor constants with `L` suffixes on masks, so consumers must use integer widths carefully when combining with 32-bit register values.

### Integration points

This header integrates with:

- KFD SDMA MQD and queue programming for GFX9, including ring controls, IB controls, doorbells, VMID assignment, and context status decoding.
- SOC15 register access code that supplies the address layer.
- Debug and fault handling paths that decode `STATUS*`, `UTCL1_*`, `GPU_IOV_VIOLATION_LOG`, EDC, and perf registers.
- Virtualization and SR-IOV flows using VF/PF, VFID, MMHUB trust level, and violation log fields.

### Risks

- Shift/mask drift is subtle. The code may still compile while writing the wrong bit, leaving queues disabled, assigning the wrong VMID, missing preemption, or corrupting pointer writeback configuration.
- Reserved fields are explicitly modeled in several registers. Code should not write arbitrary values into reserved masks unless the hardware specification requires it.
- Repeated queue layouts look identical but are not a license to ignore offset differences. Field layout and register address are separate contracts.
- SDMA 4.2.2 has a separate shift/mask header in the tree; use this 4.0 header only with 4.0 offsets and defaults.
- Some fields describe fault or security state (`GPU_IOV_VIOLATION_LOG`, `MMHUB_TRUSTLVL`, VM context fields). Misdecoding them can hide isolation failures or misattribute faults.

### Test signals

- Compile tests for KFD GFX9 code that includes this header.
- Static generation checks that every `__SHIFT` has a matching `_MASK` and that masks align with shifts and field widths.
- Runtime SDMA ring tests that verify `RB_ENABLE`, `RB_SIZE`, pointer writeback, doorbell, IB, VMID, and preemption fields produce working queues.
- Fault-injection or diagnostic tests for UTCL1 XNACK/page fault fields, EDC counters, GPU IOV violation logs, and status register decoding.
- Register dump tools should decode default values from `sdma1_4_0_default.h` through this header and produce plausible field names and values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_offset.h

### Purpose

`sdma1_4_2_2_offset.h` is the generated SDMA1 register offset map for SDMA 4.2.2 hardware. It covers the `sdma1_sdma1dec` block with base address `0x6180`. Like the 4.0 offset header, it exposes symbolic `mmSDMA1_*` register offsets and matching `_BASE_IDX` values, but this generation expands the RLC queue set and shifts some queue windows.

The file defines 507 real register offsets plus `_BASE_IDX` macros: 86 core SDMA1 registers, 43 GFX queue registers, 42 PAGE queue registers, and 336 RLC queue registers. The RLC coverage expands to RLC0 through RLC7, with the same repeated queue register layout per RLC queue.

### Important APIs, types, and functions

There are no functions or types. The public surface is:

- Include guard `_sdma1_4_2_2_OFFSET_HEADER`.
- Core offset macros such as `mmSDMA1_UCODE_ADDR`, `mmSDMA1_VM_CNTL`, `mmSDMA1_CNTL`, `mmSDMA1_STATUS_REG`, `mmSDMA1_UTCL1_CNTL`, and `mmSDMA1_GPU_IOV_VIOLATION_LOG`.
- A 4.2.2-specific `mmSDMA1_GPU_IOV_VIOLATION_LOG2` at offset `0x0062`.
- Queue windows: `GFX_RB_CNTL` at `0x0080`, `PAGE_RB_CNTL` at `0x00d8`, `RLC0_RB_CNTL` at `0x0130`, `RLC1_RB_CNTL` at `0x0188`, and additional RLC windows through `RLC7_RB_CNTL` at `0x0398`.
- Matching `*_BASE_IDX` macros, all set to `0`.

Compared with SDMA 4.0, this header drops `MMHUB_TRUSTLVL`, adds `GPU_IOV_VIOLATION_LOG2`, moves PAGE and RLC windows earlier, and increases RLC queue count from two to eight.

### Control flow

The header has no internal control flow. It feeds address calculations in SDMA 4.2.2 consumers. In this tree, `amdgpu_amdkfd_arcturus.c` includes this header and its `get_sdma_rlc_reg_offset()` function calculates queue register offsets for SDMA engines, including SDMA1 through `mmSDMA1_RLC0_RB_CNTL`. The queue offset flow then adds `queue_id * (RLC1_RB_CNTL - RLC0_RB_CNTL)` to reach the selected RLC queue window.

### State and persistence behavior

The file is stateless, but it names persistent hardware register locations:

- Microcode and control state (`UCODE_*`, `CNTL`, `CLK_CTRL`, `POWER_CNTL`, `FREEZE`, phase quantum registers).
- VM, SR-IOV, and fault state (`VM_*`, `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `VF_ENABLE`, `GPU_IOV_VIOLATION_LOG`, `GPU_IOV_VIOLATION_LOG2`).
- UTCL1/XNACK/invalidation/page-walk state.
- GFX, PAGE, and eight RLC queue windows containing ring base/pointers, IB state, doorbells, status, watermarks, preemption, AQL, and mid-command capture registers.

Changing an offset changes which hardware state a driver read or write touches, so persistence is a hardware compatibility contract rather than a software-owned variable.

### Dependencies

This header depends on:

- SOC15 register access macros and block definitions for SDMA1.
- Matching SDMA 4.2.2 SDMA0, SDMA2 through SDMA7 headers in Arcturus-style multi-SDMA-engine code.
- The matching `sdma1_4_2_2_sh_mask.h` for field definitions. This work item only maps the offset header, but the shift/mask header exists in the same directory and should be used with it.

Observed direct consumer: `amdgpu_amdkfd_arcturus.c`.

### Integration points

The central integration point is Arcturus KFD SDMA queue support. `amdgpu_amdkfd_arcturus.c` computes per-engine, per-queue RLC register offsets using SDMA engine-specific headers, and SDMA1 uses this file for engine 1. Because this generation supports eight RLC windows, queue enumeration and MQD programming can cover more SDMA queues than SDMA 4.0.

The header also integrates with register dump/debug code, SR-IOV fault handling, VM/TLB invalidation diagnostics, and any SOC15 register access path that needs SDMA1 4.2.2 symbolic offsets.

### Risks

- This header is not a drop-in replacement for SDMA1 4.0. The base address changes from `0x5180` to `0x6180`, `PAGE_RB_CNTL` moves from `0x00e0` to `0x00d8`, `RLC0_RB_CNTL` moves from `0x0140` to `0x0130`, and RLC queue spacing changes from `0x60` in 4.0 to `0x58` in 4.2.2.
- Code that assumes only RLC0/RLC1 will miss RLC2 through RLC7 on 4.2.2 hardware.
- Code that carries over `MMHUB_TRUSTLVL` from 4.0 will not find that macro here; code that ignores `GPU_IOV_VIOLATION_LOG2` may lose fault detail.
- If queue-id bounds are wrong, address arithmetic can step past `RLC7` into unrelated register space.
- All macros compile as constants, so version mixups usually fail at runtime, not at compile time.

### Test signals

- Build coverage for `amdgpu_amdkfd_arcturus.c`.
- Static checks that RLC0 through RLC7 windows are complete and evenly spaced for the expected 4.2.2 layout.
- Runtime KFD SDMA queue tests on Arcturus-class hardware across all exposed SDMA engines and queue IDs, including queues above RLC1.
- SR-IOV and VM fault tests that inspect both `GPU_IOV_VIOLATION_LOG` and `GPU_IOV_VIOLATION_LOG2`.
- Suspend/resume and GPU reset tests that reinitialize SDMA1 4.2.2 rings using the matching offset and shift/mask headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_offset.h -->
