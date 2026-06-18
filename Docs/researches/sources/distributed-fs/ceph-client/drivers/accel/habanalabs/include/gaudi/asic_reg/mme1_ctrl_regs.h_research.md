# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme1_ctrl_regs.h

## Purpose
`mme1_ctrl_regs.h` is the auto-generated register address map for the Gaudi `MME1_CTRL` block. It has the same MME prototype and register schema as `mme0_ctrl_regs.h`, but at the MME1 control base around `0xE0000`. The header names MME1 architectural descriptor, command/status/control, rate/power/debug, and shadow descriptor registers so the driver can address the second MME control block explicitly or through per-MME offset arithmetic.

## Important APIs, types, and functions
The exported API is the `mmMME1_CTRL_*` macro namespace. Important groups mirror MME0:
- `ARCH_*` live descriptor registers for tensor S/L/O base addresses, headers, convolution dimensions, iterations, loop strides, ROI sizes, spatial strides, AGU local/remote offsets, sync-object addresses/data, performance events, padding, metadata, and rate limiter saturation.
- Operational registers such as `CMD`, `STATUS1`, `RESET`, `QM_STALL`, `SYNC_OBJECT_FIFO_TH`, `EUS_ROLLUP_CNT_ADD`, `INTR_CAUSE`, `INTR_MASK`, `LOG_SHADOW`, and `PROT`.
- PCU, power, CoreSight debug, TE clock-gate, AGU counter, EZSync, and slave LBW clock-enable registers.
- Four replicated `SHADOW_0` through `SHADOW_3` descriptor banks with the same field families as the live architecture descriptor region.

There are no functions or structs. The file provides stable register names and absolute config-space addresses.

## Control flow
No executable control flow exists in the header. Runtime flow is in consumers. Gaudi initialization and tuning code writes MME rollup counters for MME0 and MME1. Idle reporting in `gaudi.c` reaches MME1 by adding `MME_QMAN_OFFSET`-based offsets to MME0 control/status addresses, then treats MME1 and MME3 as slave MMEs that require MME architecture idle status but not QMAN idle status. Security setup in `gaudi_security.c` includes `mmMME1_CTRL_BASE` in protection-block initialization and uses the MME0 schema to compute register protection masks that apply to corresponding MME control blocks.

Like MME0, actual work execution is descriptor and QMAN driven. This file names the control and descriptor visibility registers for MME1; it does not implement descriptor creation or queue scheduling.

## State and persistence behavior
The file owns no software state. It addresses hardware state in MME1: active descriptor fields, shadow descriptor snapshots, command/status/reset/stall state, interrupt cause/mask state, protection settings, PCU/rate/power controls, debug counters, and AGU/sync counters. Those hardware fields persist until MME reset, device reset, security reprogramming, or explicit driver writes.

The MME1 map is persistent generated data for the ASIC revision. The consistency between `MME0_CTRL` and `MME1_CTRL` layouts is especially important because driver code often reasons about MMEs as repeated engines.

## Dependencies and integration points
This header is included through `gaudi_regs.h`. It integrates with:
- `gaudi.c`, which writes `mmMME1_CTRL_EUS_ROLLUP_CNT_ADD` and reports MME idle state for repeated engines.
- `gaudi_security.c`, which configures protection blocks for `mmMME1_CTRL_BASE`.
- `gaudi_coresight.c`, indirectly through MME1 control block debug bases for STM, ETF, BMON, and SPMU operations.
- MME QMAN setup and reset flows, because MME1 is a slave MME paired with a master QMAN block rather than owning a distinct full QMAN path in the same way as master MMEs.

Consumers must preserve the distinction between MME control block numbering and QMAN master/slave topology. MME1 control status is real even when QMAN status is checked only for master MME indices.

## Risks and edge cases
- The file is almost entirely parallel to MME0 with a different base. Copy/paste assumptions are useful but dangerous if a future generated map introduces a real MME1-only deviation.
- Idle reporting treats odd MMEs as slaves and skips QMAN status for them. If topology changes, this assumption can hide a stuck QMAN or misclassify idle state.
- Security/protection setup relies on block-base protection and MME0-derived field groupings. Register movement in MME1 could require dedicated masks.
- CoreSight register-index arrays must map MME1 debug bases to MME1, not MME0. Base-address drift would make debug tools inspect or program the wrong MME.
- Shadow descriptor registers are repetitive and large; errors can affect debug visibility and protected-register windows without obvious compile-time failures.
- As with MME0, writes to descriptor/control registers are hardware-sensitive and need reset/debug-mode discipline.

## Test signals
Positive signals include MME1 rollup counter programming during initialization, idle reports showing plausible MME1 `ARCH_STATUS`, successful MME workloads involving paired MME engines, no protection faults for allowed MME1 accesses, correct CoreSight targeting of MME1 blocks, and clean reset behavior. Negative signals include MME1 stuck non-idle while its paired master QMAN is idle, protection-bit errors under `MME1_CTRL`, wrong-engine CoreSight trace data, unexpected MME1 interrupts, or mismatched behavior between MME0/MME1 on symmetric workloads.
