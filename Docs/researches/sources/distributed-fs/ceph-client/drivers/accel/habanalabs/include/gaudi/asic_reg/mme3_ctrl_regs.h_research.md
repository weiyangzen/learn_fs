# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme3_ctrl_regs.h

## Purpose

`mme3_ctrl_regs.h` is the auto-generated hardware register address map for the Gaudi MME3 control block, also marked as prototype `MME`. It exports 717 `mmMME3_CTRL_*` constants from `mmMME3_CTRL_ARCH_STATUS` at `0x1E0000` through `mmMME3_CTRL_SHADOW_3_DESC_DUMMY` at `0x1E0DA4`. Its normalized macro layout matches `mme2_ctrl_regs.h`; the meaningful difference is the MME3 prefix and address range.

## Important APIs, types, and functions

There are no functions, structs, or runtime helpers. The exported API is the set of register address macros:

- Active `ARCH_*` descriptor registers describe the live descriptor image for MME3, including tensor S/L/O geometry, AGU offsets, convolution parameters, iteration controls, sync-object fields, padding, metadata, performance selectors, and rate limiting.
- `SHADOW_0_*` through `SHADOW_3_*` provide four replicated descriptor banks with the same field families as `ARCH_*`.
- Control and debug definitions include command/reset/protection, interrupt cause/mask, QM slave and stall controls, AGU sync/state-machine registers, TE close, PCU and EUS control/status, power, and sync-object related addresses.

## Control flow

This header has no executable control flow. Consumer code drives control flow by writing descriptors, commands, and control bits to these addresses. `gaudi_coresight.c` references MME3 control block base constants for STM, ETF, BMON, and SPMU arrays; `gaudi.c` writes MME3-specific control registers such as EUS rollup where needed. MME3 compute work is coordinated with QMAN programming from separate QMAN headers and with descriptor/control state exposed here.

## State and persistence behavior

The defines are compile-time constants. The addressed MME3 registers are volatile hardware state. Descriptor and shadow banks persist in the device until overwritten or reset; command, interrupt, protection, and power-control registers affect current hardware execution state. Because the active and shadow descriptor layouts are replicated, correct persistence depends on writing the intended bank and field consistently throughout descriptor lifecycle operations.

## Dependencies and integration points

The file is included by `gaudi_regs.h` and consumed by Gaudi driver paths that need MME3 control addresses. It is tightly coupled to `mme2_ctrl_regs.h` by layout symmetry and to generated block/base headers used by CoreSight and monitoring code. It also integrates with MME queue-manager setup indirectly: QMANs submit work, while this control bank exposes descriptor and engine-control registers used by the MME hardware executing that work.

## Risks

The chief risk is silent hardware misprogramming from generated address mismatch. Since MME2 and MME3 layouts are identical after prefix/base normalization, accidental cross-instance use compiles cleanly but touches the wrong engine. Descriptor banks have many fields with similar names; wrong bank or tensor suffix errors can corrupt compute addressing and be hard to attribute. Lack of field masks in this file means bit-level correctness depends on other generated headers and hardware validation.

## Test signals

Expected signals include successful driver build, Gaudi probe with MME3 present, MME workloads that schedule onto the MME3 engine path, descriptor/shadow-bank programming tests, MME3 interrupt/status handling, and CoreSight/debug enumeration for MME3 STM/ETF/BMON/SPMU blocks. A useful static test is a normalized diff against `mme2_ctrl_regs.h` to confirm the register sequence remains identical while base addresses differ intentionally.
