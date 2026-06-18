# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ti-k3.c

Purpose: Texas Instruments K3/AM62 RTC driver. It supports 48-bit seconds, alarm, offset calibration, scratch-register nvmem, unlock/synchronization fences across clock domains, erratum i2327 handling, wakeup, and low-power resume reconfiguration.

Important APIs/types/functions: `struct ti_k3_rtc` stores IRQ, sync timeout, 32 kHz rate, RTC device, regmap, and regmap fields. `k3rtc_field_read/write()`, `k3rtc_fence()`, and `k3rtc_unlock_rtc()` abstract register field access and 32 kHz domain synchronization. `k3rtc_configure()` enforces erratum requirements, enables oscillator-dependent sync, sets counter freeze mode, clears/disables IRQs, and fences. RTC ops read/write 48-bit time, alarm compare, alarm IRQ enable, and ppb offset through compensation register math. `ti_k3_rtc_interrupt()` handles delayed status clear/reload sequencing for 32 kHz-domain IRQ deassertion. NVMEM callbacks expose scratch registers.

Control flow/state/persistence: probe maps MMIO regmap, allocates fields, enables `osc32k` and `vbus` clocks, gets IRQ, allocates RTC with 48-bit range, requests threaded IRQ, configures hardware, marks wakeup capable/source, registers RTC, then registers nvmem. Resume reconfigures if RTC is locked, indicating low-power context loss.

Dependencies/integration: compatible `ti,am62-rtc`, regmap MMIO/fields, `sys_soc` erratum match, clocks `osc32k` and `vbus`, threaded IRQ, RTC core offset API, nvmem, PM wake.

Risks/test signals: AM62X SR1.0 requires bootloader unlock; Linux refuses operation if locked. Field operations cannot be used for some writes due to freeze/race behavior. Test erratum matched/unmatched paths, non-32768 clock warning and timeout calculation, fence timeouts, IRQ status clear/reload sequence, offset min/max conversion, scratch nvmem alignment, and resume after context loss.
