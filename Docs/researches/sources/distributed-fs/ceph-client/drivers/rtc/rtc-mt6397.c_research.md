# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mt6397.c

Purpose: provides RTC support for MediaTek MT6397-family PMICs over the parent MFD regmap, covering time, one-shot alarm, pending power-on alarm state, and wake IRQs.

Important APIs/types/functions: `struct mt6397_rtc` is defined in the MT6397 RTC header and used here for regmap, base address, match data, mutex, IRQ, and RTC device. `mtk_rtc_write_trigger()` writes the variant-specific WRTGR and polls `RTC_BBPU_CBUSY`. `mtk_rtc_irq_handler_thread()` reports alarm events and disables alarm IRQ. Bulk time/alarm callbacks use `RTC_OFFSET_*` indexes and masks from `linux/mfd/mt6397/rtc.h`.

Control flow: probe gets parent `mt6397_chip`, uses the memory resource start as `addr_base`, gets match data for WRTGR offset, requests the alarm IRQ, enables wakeup, sets a 1900-2027 range with start-time correction from 1968-01-02, and registers. Reads bulk-read time fields under a mutex and retry if seconds carry. Set-time increments month and weekday to hardware's one-based encoding, bulk-writes the fields, then triggers. Set-alarm reads current alarm registers, overlays masked fields, writes them only when enabling, sets the DOW mask and one-shot enable bit, then triggers.

State and persistence: hardware registers persist time, alarm, IRQ enable/status, PDN2 power-on alarm flag, and BBPU busy state. Driver state has a mutex and variant data but no alarm cache. The IRQ handler disables alarm enable after firing, making alarms one-shot.

Dependencies and integration: depends on MT6397 MFD parent data/regmap, OF compatibles `mediatek,mt6323-rtc`, `mt6357-rtc`, `mt6358-rtc`, and `mt6397-rtc`, variant WRTGR offsets, threaded high-triggered IRQ, and PM wake hooks.

Risks and test signals: `mtk_rtc_set_time()` and set-alarm mutate the caller-provided `rtc_time` month/weekday in place. The IRQ handler computes `irqen = irqsta & ~RTC_IRQ_EN_AL`, which uses status bits as the new enable value and deserves hardware-specific validation. Set-alarm with `enabled == false` does not rewrite alarm time fields, only clears one-shot. Test all compatibles, WRTGR poll timeout, regmap errors, month/weekday one-based conversions, power-on alarm pending flag, one-shot disable after IRQ, and suspend wake calls.
