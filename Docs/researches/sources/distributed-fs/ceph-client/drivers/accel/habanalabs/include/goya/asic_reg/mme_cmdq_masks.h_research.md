# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_cmdq_masks.h

## Purpose

`mme_cmdq_masks.h` defines generated bit shifts and masks for the Goya MME command-queue (`MME_CMDQ`) register block. It complements `mme_cmdq_regs.h`: that file names register offsets, while this file names the fields packed into each 32-bit register.

## Important APIs, types, and data

The file exports `MME_CMDQ_*_SHIFT` and `MME_CMDQ_*_MASK` macros. Important field groups include global enables for PQF, CQF, CP, and DMA; stop/flush bits; protection and error-protection bits; error interrupt/message/stop-on-error controls; error address/write-data capture fields; secure and non-secure ASID/MMBP properties; global idle/stop/error status; CQ credit and max-inflight fields; CQ pointer/size/control and mirrored status fields; CQ credit/free/inflight/busy/empty status; read-rate limiter token/saturation/timeout fields; CP message-base addresses; LDMA descriptor offset registers; four fence read-data and count registers; CP ready/stop/fence status bits; current instruction low/high fields; barrier guard bits; and CQ debug buffer access fields.

There are no types or functions. All full-width address/data fields use `0xFFFFFFFF`, small counters use narrow masks such as `0xFFFF`, `0xFF`, `0xF`, or `0x3`, and control flags occupy individual bits.

## Control flow

No executable control flow is present. Consumers combine shifts and masks when constructing values for `WREG32()` or decoding values from `RREG32()`. A typical queue setup flow writes secure/non-secure properties, CQ pointer/size/control registers, CP message bases, LDMA offsets, error configuration, protection bits, and finally enables the command queue. Error or reset flow reads status/error fields, may request stop/flush, waits for idle/stop status, and clears or reinitializes state.

## State and persistence behavior

The macros themselves are stateless. The hardware fields they describe control persistent device state for the lifetime of the current queue configuration: ASID/MMBP security context, command buffer location, CP message routing, rate limiting, fence counters, and stop-on-error behavior. Error capture fields are latched hardware state until cleared by the corresponding device logic.

## Dependencies and integration points

This header integrates with `mme_cmdq_regs.h`, common queue-management code, and Goya MME command submission. It shares the same CMDQ prototype field layout as other HabanaLabs command queue blocks. Driver code must use the masks with the matching MME_CMDQ offsets; mixing them with QMAN offsets is only safe where the underlying CMDQ/QMAN prototype fields are intentionally identical.

## Risks and edge cases

Field packing is dense in global config, status, and CP status registers. Incorrect shifts can enable DMA/CP without the queue frontend, fail to stop on errors, or misdecode busy/idle state. ASID fields are 10 bits; truncation or stale ASID programming can route transactions through the wrong address space. Fence counters and increment values are narrow and can wrap if interpreted as full 32-bit counters. Full-width pointer fields are split across low/high registers and must be updated coherently.

## Test signals

Compile-time tests should verify every referenced MME_CMDQ field macro exists. Runtime signals include successful MME command queue initialization, correct idle/stop transitions on reset, expected CP fence behavior, no unexpected CQ busy/empty deadlocks, and accurate error logs when injected malformed or unauthorized command queue accesses trip `GLBL_STS1` or error capture registers.
