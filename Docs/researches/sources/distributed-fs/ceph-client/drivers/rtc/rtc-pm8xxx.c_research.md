# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pm8xxx.c

Purpose: implements the Qualcomm PM8xxx/PMIC RTC block for several PMIC register layouts. It supports raw 32-bit seconds counters, alarms, wake IRQs, optional direct hardware time setting, and an offset model that persists wall-clock offset in NVMEM or a Qualcomm UEFI variable.

Important APIs/types/functions: `struct pm8xxx_rtc_regs` describes per-PMIC register addresses and alarm enable bits; `struct pm8xxx_rtc` stores regmap, offset storage, policy flags, and RTC state. `pm8xxx_rtc_read_raw()` reads the four-byte counter safely across LSB carry. `__pm8xxx_rtc_set_time()` performs the hardware write sequence when allowed. `pm8xxx_rtc_update_offset()` derives and persists offset when direct set-time is disabled. `pm8xxx_rtc_read_time()` adds offset to raw seconds; `pm8xxx_rtc_set_alarm()` subtracts it before programming hardware. `pm8xxx_alarm_trigger()` reports and clears alarm IRQs.

Control flow: probe matches OF compatible to register layout, obtains parent regmap, optionally gets the alarm IRQ unless `qcom,no-alarm`, reads offset storage when direct set-time is not allowed, enables the RTC, allocates/configures the RTC, requests alarm IRQ and wake IRQ if available, and registers the device. Shutdown flushes small dirty offset changes that were deferred to reduce flash wear.

State and persistence: raw RTC seconds are stored in PMIC registers. The Linux-visible time is raw seconds plus `offset` unless `allow-set-time` programs raw hardware directly. Offset can persist in an NVMEM cell or in EFI variable `RTCInfo`, converted between GPS and Unix offsets. Alarm registers store raw-time alarm seconds.

Dependencies and integration: depends on platform/OF matching, parent PMIC regmap, RTC core, nvmem consumer API, optional EFI variable support, PM wake IRQ, and unaligned little-endian helpers. Compatible data covers PM8921, PM8058, PM8941, and PMK8350 layouts.

Risks: offset arithmetic uses 32-bit seconds and can wrap for far future dates. Dirty offsets under 30 seconds are only persisted at shutdown, so sudden power loss can lose drift correction. EFI variable availability may defer probe, and the write path depends on runtime EFI services. Alarm pending is not surfaced in `read_alarm()`. Test signals include raw carry re-read, direct and offset set-time modes, NVMEM and UEFI offset read/write, dirty-offset shutdown flush, alarm IRQ clear, `qcom,no-alarm`, wake IRQ, and each compatible register map.
