# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_0_sh_mask.h

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
