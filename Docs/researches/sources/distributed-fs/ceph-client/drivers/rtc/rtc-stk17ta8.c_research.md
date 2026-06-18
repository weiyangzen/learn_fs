# sources/distributed-fs/ceph-client/drivers/rtc/rtc-stk17ta8.c

Purpose: platform RTC and NVRAM driver for Simtek STK17TA8 battery-backed SRAM/RTC. It supports BCD time, alarm interrupts, voltage-low warning, oscillator start, and nvmem access to the SRAM window before the RTC register block.

Important APIs/types/functions: `struct rtc_plat_data` stores RTC, MMIO, last read jiffies, IRQ, alarm masks, cached alarm fields, and lock. Time ops use `RTC_READ`/`RTC_WRITE` flags around register access and include a century register. `stk17ta8_rtc_update_alarm()` writes alarm fields, using `0x80` as wildcard or update interrupt encoding. The IRQ handler distinguishes alarm vs update events by checking `RTC_SECONDS_ALARM`. NVMEM callbacks read/write byte ranges directly.

Control flow/state/persistence: probe maps the whole device, starts the RTC if `RTC_STOP` is set, warns on power-fail, requests shared IRQ if available, allocates RTC, registers battery-backed nvmem, and registers RTC. Alarm settings are cached in RAM but programmed into hardware on updates.

Dependencies/integration: platform name `stk17ta8`, MMIO, shared IRQ, BCD helpers, RTC core, `devm_rtc_nvmem_register()`.

Risks/test signals: if no IRQ is available alarm ops return `-EINVAL`. Read path sleeps 1 ms when called in the same jiffy to avoid continuous-read update issues. Test oscillator-stop recovery, voltage-low reporting, century conversion, wildcard alarm fields, update-vs-alarm interrupt reporting, nvmem boundaries, and IRQ absent behavior.
