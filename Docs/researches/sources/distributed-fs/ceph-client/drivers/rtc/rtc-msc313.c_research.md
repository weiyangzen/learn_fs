# sources/distributed-fs/ceph-client/drivers/rtc/rtc-msc313.c

Purpose: supports the MStar/SigmaStar MSC313 RTC, a 32-bit seconds counter with match-alarm registers and clock-rate programming.

Important APIs/types/functions: `struct msc313_rtc` stores the RTC device and MMIO base. Alarm callbacks use `REG_RTC_MATCH_VAL_L/H` and `INT_MASK_BIT`; time callbacks use load and count registers plus `LOAD_EN_BIT`, `READ_EN_BIT`, and `CNT_EN_BIT`. `msc313_rtc_interrupt()` checks `ALM_INT_BIT`, clears interrupt state through control bits, and reports `RTC_AF`.

Control flow: probe maps the register block, obtains IRQ 0, allocates the RTC, requests a shared IRQ, enables the input clock, writes the clock rate into frequency control registers, stores private data, and registers the RTC. Reads fail with `-EINVAL` if the counter is not enabled, then set `READ_EN_BIT` and busy-wait until the hardware latches count registers. Set-time writes split load value, sets `LOAD_EN_BIT`, busy-waits until it clears, then enables counting. Alarm setup writes split match value and masks/unmasks the interrupt.

State and persistence: persistent hardware state includes frequency control, count, load, match, enable, interrupt mask, and status bits. Driver state is only MMIO and RTC pointer. There is no explicit range beyond U32 seconds and no wakeup setup.

Dependencies and integration: depends on OF compatible `mstar,msc313-rtc`, platform MMIO, one clock, one shared IRQ, and RTC class alarm APIs.

Risks and test signals: the read and load latch waits are unbounded busy loops with only `udelay(1)`, so hardware stuck bits can hang the caller. Alarm enabled defaults to zero unless unmasked; `read_alarm()` does not report pending status. Test disabled-counter read failure, latch completion, stuck latch behavior, clock-rate split programming, shared IRQ returning `IRQ_NONE` for non-alarm status, alarm mask polarity, and U32 wrap behavior.
