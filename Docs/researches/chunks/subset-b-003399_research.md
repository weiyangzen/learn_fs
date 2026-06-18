# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma6/sdma6_4_2_2_sh_mask.h lines 1-2569

## Scope

This chunk is the first 2,569 lines of AMDGPU's generated SDMA6 4.2.2 register field header. It contains C preprocessor constants only: each register field is described by a `__SHIFT` macro and a matching `_MASK` macro. There are no functions, structs, enums, storage objects, executable branches, or inline helpers in this slice.

The requested range starts at the license/header guard and the `sdma6_sdma6dec` address block. It covers public SDMA6 control/status registers, VM and virtualization fields, UTCL1/XNACK/page-fault related fields, performance/error/IOV fields, the GFX and PAGE queue register sets, RLC queue register sets `RLC0` through `RLC4`, and most of the `RLC5` queue register set. The chunk ends exactly at `SDMA6_RLC5_MIDCMD_DATA8__DATA8_MASK`; `SDMA6_RLC5_MIDCMD_CNTL` and the later `RLC6`/`RLC7` queue blocks are outside this work item.

## Purpose

The file provides bit layout metadata for the sixth SDMA engine instance on ASICs using the SDMA 4.2.2 register map. Driver code combines these masks and shifts with the matching address constants from `sdma6_4_2_2_offset.h` and AMDGPU register helpers to program or decode SDMA hardware registers.

This chunk describes fields for:

- SDMA microcode address/data and checksum registers.
- VM context, active function ID, VF enablement, and virtual reset request registers.
- Context/public register type bitmaps that classify which SDMA registers are context-owned or public.
- Main SDMA control, clock, power, chicken-bit, GB address, burst, freeze, phase quantum, EDC, atomic, and status registers.
- UTCL1 controls, watermarks, read/write status, invalidation registers, XNACK address/vector logging, timeout limits, and page request attributes.
- Error, physical address, GPU IOV violation, ULV, EA double-bit address, credit, performance monitor, and dummy/debug registers.
- Queue programming surfaces for `GFX`, `PAGE`, and `RLC0`-`RLC5`: ring-buffer control/base/read-pointer/write-pointer registers, write-pointer polling, indirect-buffer control/base/size/read-pointer registers, context status, doorbell controls/logs/offsets, context-save-area addresses, preemption, watermark, AQL, minor pointer update, and mid-command data capture.

## Important APIs, Types, and Constants

There are no C APIs or types declared here. The public interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Representative constants include:

- `SDMA6_CNTL__TRAP_ENABLE_MASK`, `SDMA6_CNTL__UTC_L1_ENABLE_MASK`, `SDMA6_CNTL__AUTO_CTXSW_ENABLE_MASK`, and interrupt enable masks for SDMA control.
- `SDMA6_STATUS_REG__IDLE_MASK`, `SDMA6_STATUS_REG__RB_EMPTY_MASK`, `SDMA6_STATUS_REG__INSIDE_IB_MASK`, `SDMA6_STATUS_REG__SEM_RESP_STATE_MASK`, and related engine-idle/stall indicators.
- `SDMA6_UTCL1_CNTL__REDO_ENABLE_MASK`, `SDMA6_UTCL1_RD_STATUS__PAGE_FAULT_MASK`, `SDMA6_UTCL1_WR_STATUS__PAGE_NULL_MASK`, and `SDMA6_UTCL1_INV0__INV_VMID_VEC_MASK`.
- `SDMA6_GPU_IOV_VIOLATION_LOG__VIOLATION_STATUS_MASK`, `...__ADDRESS_MASK`, `...__VF_MASK`, and `...__VFID_MASK`.
- Queue setup fields such as `SDMA6_GFX_RB_CNTL__RB_ENABLE_MASK`, `SDMA6_PAGE_IB_CNTL__IB_ENABLE_MASK`, `SDMA6_RLC0_RB_WPTR_POLL_CNTL__FREQUENCY_MASK`, and `SDMA6_RLC5_DOORBELL__ENABLE_MASK`.
- Address alignment masks such as `SDMA6_GFX_IB_BASE_LO__ADDR_MASK`, `SDMA6_PAGE_RB_RPTR_ADDR_LO__ADDR_MASK`, and the analogous `RLC*` address fields.

The repeated queue blocks are structurally important. `GFX`, `PAGE`, and each `RLCn` queue use nearly identical field layouts for RB/IB setup, doorbells, writeback addresses, status, AQL, and mid-command data. That regularity is relied on by code that derives per-queue offsets instead of hard-coding every queue register.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants that are substituted into AMDGPU register helper calls.

Runtime behavior appears in consumers that combine:

- An address macro such as `mmSDMA6_UTCL1_TIMEOUT` or `mmSDMA6_RLC0_RB_CNTL` from `sdma6_4_2_2_offset.h`.
- A field namespace from this file, for example `SDMA6_RLC0_RB_CNTL`.
- Register read/write or field helpers such as `RREG32`, `WREG32`, `SOC15_REG_OFFSET`, `SOC15_REG_GOLDEN_VALUE`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

The nearby AMDGPU SDMA implementation (`amdgpu/sdma_v4_0.c`) includes this header with the matching offset header and uses the SDMA register namespaces for register lists and golden settings. The KFD Arcturus bridge (`amdgpu/amdgpu_amdkfd_arcturus.c`) includes SDMA0-SDMA7 register headers and computes RLC queue offsets by using the distance between queue register blocks.

## State and Persistence Behavior

The header stores no software state and performs no persistence itself. The fields it names map to SDMA hardware register state while the GPU block is powered and accessible.

Control fields can alter persistent hardware behavior until reset, power-gating loss, or later driver reprogramming. Examples include microcode upload address/data, VM context settings, VF enable/reset fields, SDMA enable/control bits, clock and memory-power controls, UTCL1 redo/invalidation/page controls, ring/IB enable bits, write-pointer polling controls, doorbell enable/offset fields, context-save addresses, AQL settings, and preemption controls.

Status and log fields expose volatile or sticky hardware-observed state. Examples include engine idle/full/stall bits, UTCL1 read/write FIFO and page fault status, XNACK address/vector logs, EDC counters, performance counter results, GPU IOV violation logs, doorbell logs, write-pointer update pending/failure counts, context selected/idle/expired/preempted bits, and mid-command data registers. This header does not encode whether a field is read-only, write-one-to-clear, clear-on-read, sticky, or latched; call sites must follow the hardware register specification.

## Dependencies

Primary dependencies and companions:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma6/sdma6_4_2_2_offset.h` supplies the matching `mmSDMA6_*` addresses and base indices. Its address block starts at base address `0x7c000`, with `mmSDMA6_GFX_RB_CNTL` at offset `0x0080`, `mmSDMA6_PAGE_RB_CNTL` at `0x00d8`, and RLC queue blocks starting at `mmSDMA6_RLC0_RB_CNTL` offset `0x0130`.
- AMDGPU's generated register-field macros expect the exact mask/shift naming convention used here. `REG_SET_FIELD` and `REG_GET_FIELD` form field values by token-pasting the register and field names to these macros.
- SOC15 register access helpers use the offset header and hardware IP instance to map the SDMA6 local register offset into the device register aperture.
- Sibling SDMA headers (`sdma0` through `sdma7`) provide matching layouts for other SDMA engine instances. `amdgpu_amdkfd_arcturus.c` includes all of them because Arcturus exposes multiple SDMA engines.
- `amdgpu/sdma_v4_0.c` includes this header and uses SDMA register names in diagnostic register lists and ASIC-specific golden register tables.

## Integration Points

This chunk sits at the generated hardware-description boundary, not in a high-level Ceph or filesystem path despite the repository prefix. Its practical consumers are AMDGPU SDMA/KFD paths.

Integration points include:

- SDMA initialization and golden setting application, where masks/addresses are used to program timing, polling, UTCL1, GB address, and queue-control registers.
- Queue setup for graphics, page, and KFD/RLC queues, where RB/IB bases, sizes, read/write pointers, VMID/privilege, doorbells, AQL, CSA, and writeback addresses must be encoded exactly.
- Runtime diagnostics and debug register dumps, where status, XNACK, page-fault, doorbell, and mid-command fields are decoded.
- GPU virtualization and SR-IOV support, where active function IDs, VF enablement, virtual reset requests, and IOV violation logs are interpreted.
- Error handling and RAS-adjacent paths, where EDC counters, page fault/null status, error logs, physical address registers, and EA double-bit address registers may be read.

## Risks

- Any incorrect mask or shift silently programs the wrong hardware bits. For queue registers this can corrupt ring base addresses, pointer writeback addresses, VMID/privilege, doorbell routing, AQL packet stepping, or IB execution state.
- Address fields have alignment baked into the masks and shifts, commonly low-bit offsets of `0x2` or `0x5`. Call sites must pass already-compatible addresses and avoid treating masked fields as byte-exact full addresses.
- The repeated queue layout makes copy/paste or generator errors hard to spot: a typo in an `RLCn` field can affect only one queue while the others continue to work.
- This chunk boundary is in the middle of the `RLC5` queue block. Research or reconciliation that assumes complete RLC5 coverage from this chunk alone would miss `SDMA6_RLC5_MIDCMD_CNTL` and all later RLC6/RLC7 fields.
- Status/log fields can have write-sensitive clear semantics, but this header does not distinguish safe read fields from write-one-to-clear or hardware-owned fields.
- The SDMA6 namespace is ASIC-version-specific. Reusing these constants with another SDMA generation or engine instance can misprogram registers even when names look similar.
- Virtualization fields and IOV violation logs are security-sensitive: wrong masks can misidentify a VF, miss a violation, or incorrectly reset/enable functions.

## Test Signals

Useful verification signals for this chunk are mostly compile-time and hardware-runtime oriented:

- AMDGPU builds that include `amdgpu/sdma_v4_0.c` and `amdgpu/amdgpu_amdkfd_arcturus.c` should compile without undefined SDMA6 field macros or macro redefinition warnings.
- Generated-header consistency checks should confirm that every `<REGISTER>__<FIELD>_MASK` in lines 1-2569 has the expected companion `<REGISTER>__<FIELD>__SHIFT`, and that masks align with shifts inside 32-bit registers.
- Cross-check this header against `sdma6_4_2_2_offset.h` so field groups match address groups, especially the `GFX`, `PAGE`, and `RLC0`-`RLC5` queue block spacing.
- Runtime smoke tests on affected AMDGPU hardware should cover driver probe, SDMA microcode load, SDMA ring creation, IB submission, doorbell writes, page queue activity, suspend/resume, and GPU reset.
- KFD tests on Arcturus-like multi-SDMA hardware should exercise queue offsets for SDMA6 RLC queues and verify that queue IDs map to the expected `RLCn` register block.
- Fault or stress tests should monitor UTCL1 page fault/XNACK status, IOV violation logs, EDC counters, and performance counters without adjacent-field corruption after read-modify-write operations.
