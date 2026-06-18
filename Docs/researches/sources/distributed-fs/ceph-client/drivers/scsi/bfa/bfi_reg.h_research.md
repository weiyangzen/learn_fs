# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi_reg.h

## Purpose

`bfi_reg.h` is a hardware register definition header for QLogic/Brocade BR-series Fibre Channel adapter ASICs. It contains MMIO offsets and bit-field masks/shifts for host function interrupt registers, PLL control, host semaphores, LPU command/status and mailbox registers, PSS control, personality registers, Catapult-2 register remaps, interrupt bit assignments, firmware heartbeat/state semaphores, queue-number helpers, and PSS scratch-memory paging helpers. The file has no executable functions; it is a stable hardware ABI map consumed by low-level BFA/BNA code.

## Important APIs, Types, and Definitions

Important groups include `HOSTFN*_INT_STATUS`, `HOSTFN*_INT_MSK`, `HOST_PAGE_NUM_FN*`, `APP_PLL_LCLK_CTL_REG`, `APP_PLL_SCLK_CTL_REG`, `CT2_APP_PLL_*`, `HOST_SEM*`, `HOST_SEM*_INFO_REG`, `HOSTFN*_LPU*_CMD_STAT`, `LPU*_HOSTFN*_CMD_STAT`, mailbox offsets, `PSS_CTL_REG`, GPIO/LMEM/LPU reset bits, `FNC_PERS_REG`, `CT2_HOSTFN_PERSONALITY*`, and `__HFN_INT_*` masks. Function-like macros compose fields and queue/page numbers, including `CPE_Q_NUM()`, `RME_Q_NUM()`, `PSS_SMEM_PGNUM()`, and `PSS_SMEM_PGOFF()`.

## Control Flow

There is no local control flow. Runtime users select ASIC-family-specific offsets, program PLL/reset registers, poll lock/ready bits, claim semaphores, post mailbox commands, map function interrupts to CPE/RME queues, and page into PSS scratch memory through these constants. Comments identify `cb/ct`, `ct`, and `ct2` register families.

## State and Persistence Behavior

The file stores no state. It names persistent hardware state held in adapter registers: firmware heartbeat and state semaphores, firmware use count, fail synchronization state, queue interrupt state, mailbox state, PLL lock state, NFC/flash controller state, and PSS memory paging.

## Dependencies and Integration Points

The header integrates with BFA IOC initialization, reset, interrupt, mailbox, firmware-state, and memory-window code. It depends only on preprocessor definitions, but semantically depends on the ASIC programming guide and firmware expectations.

## Risks and Edge Cases

Wrong offsets, masks, or shifts silently break hardware access. CT2 moved semaphore and interrupt registers, so callers must not mix CT and CT2 constants. Users must handle MMIO access width and endian conversion consistently. `__APP_PLL_LCLK_FBCNT(_v)` references the SCLK shift name, which deserves caution even if the shifts are currently identical.

## Test Signals

Validate by probing each ASIC family, observing firmware boot and heartbeat/state transitions, mailbox round trips, per-function queue interrupts, CT2 semaphore reads, PLL lock polling, PSS scratch-memory access, and injected LPU/PSS/LL halt interrupt bits.
