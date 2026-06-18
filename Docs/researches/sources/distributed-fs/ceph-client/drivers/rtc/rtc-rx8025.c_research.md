<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8025.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8025.c

Purpose: implements Epson RX8025 and RX8035 I2C RTCs with time, minute-resolution daily alarm, oscillator validity checks, digital offset calibration, IRQ reporting, and a deprecated sysfs clock-adjust alias.

Important APIs/types/functions: `struct rx8025_data` stores the RTC, model, cached `ctrl1`, and 24-hour mode. SMBus helpers read/write single or block registers using the chip's shifted register address format. `rx8025_check_validity()`, `rx8025_reset_validity()`, `rx8025_init_client()`, `rx8025_read_offset()`, and `rx8025_set_offset()` handle status and calibration. RTC ops cover time, alarm, alarm IRQ enable, and offset.

Control flow: probe checks SMBus capabilities, identifies model, initializes control/status, allocates RTC, requests optional IRQ, sets minute-alarm feature and clears update-interrupt feature, adds sysfs `clock_adjust_ppb`, and registers. Reads reject PON or stopped oscillator, with opposite XST polarity for RX8025 versus RX8035, then decode BCD. Set-time writes BCD fields and clears validity flags. Alarm operations program minute/hour only and toggle `DALE` in cached control state.

State and persistence: hardware stores time, alarms, control/status flags, digital offset, and alarm enable bits. Driver state caches `ctrl1` and hour mode derived from control or RX8035 hour register.

Dependencies and integration points: depends on I2C SMBus byte/block access, RTC core, sysfs attribute group, BCD helpers, and I2C IDs. It has no OF match table in this file.

Risks and test signals: IRQ handler appears to clear `DAFG` by assigning `status &= RX8025_BIT_CTRL2_DAFG`, which can leave only the alarm bit rather than clearing it. Year range is set to 1900-2099 while set-time subtracts 100. Test RX8025/RX8035 XST polarity, 12/24-hour conversion, alarm IRQ flag clearing, offset saturation and deprecated sysfs sign inversion, PON/VDET reset, missing IRQ behavior, and writes of read-only bits noted in comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8025.c -->
