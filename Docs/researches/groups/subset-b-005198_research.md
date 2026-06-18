# subset-b-005198 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1511.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1511.c

Purpose: implements a platform RTC driver for the Dallas DS1511 timekeeper, including calendar access, alarm interrupts, and the chip's battery-backed RAM as an nvmem provider. It also performs limited watchdog cleanup by zeroing the watchdog counters during probe, but does not expose a full watchdog device.

Important APIs/types/functions: `struct ds1511_data` stores the RTC, mapped I/O base, IRQ, and alarm lock. The `rtc_class_ops` methods are `ds1511_rtc_read_time()`, `ds1511_rtc_set_time()`, `ds1511_rtc_read_alarm()`, `ds1511_rtc_set_alarm()`, and `ds1511_rtc_alarm_irq_enable()`. Register helpers `rtc_read()` and `rtc_write()` use the global `ds1511_base` and `reg_spacing`. `ds1511_nvram_read()` and `ds1511_nvram_write()` expose 256 bytes of RAM through `devm_rtc_nvmem_register()`.

Control flow: probe maps the register resource, obtains an optional IRQ, enables the oscillator/update path, clears watchdog counters, checks low-battery status, allocates/registers the RTC, optionally requests a shared IRQ, and registers nvmem. Time reads and writes stop updates around BCD register access. Alarm writes program day/hour/min/sec match registers, update the timer interrupt enable bit, and clear pending flags by reading control A. The IRQ handler reads control A to clear the interrupt and reports `RTC_IRQF | RTC_AF`.

State and persistence: calendar, alarm, and NVRAM contents persist in DS1511 battery-backed hardware. Runtime-only state is limited to the platform data object, IRQ availability, locks, and global mapped base. Alarm support is cleared from RTC features when no IRQ is usable.

Dependencies and integration: depends on platform resources, MMIO byte access, RTC core, nvmem, BCD helpers, and optional IRQ delivery. `MODULE_ALIAS("platform:ds1511")` supports platform binding.

Risks and test signals: the global `ds1511_base` makes multiple instances unsafe despite per-device allocation. Time operations use the global `ds1511_lock`, while alarm operations use `ds1511->lock`; register access serialization is therefore split. Test with no IRQ, shared IRQ, low-battery flag, NVRAM reads/writes across boundaries, alarm delivery/disable, and read/write rollover while updates are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1511.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1553.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1553.c

Purpose: supports the Dallas DS1553 memory-mapped RTC/NVRAM device. The final register window holds clock, alarm, control, watchdog, and status registers; the preceding address space is exported as battery-backed nvmem.

Important APIs/types/functions: `struct rtc_plat_data` tracks the RTC device, mapped I/O, IRQ, cached alarm fields, interrupt enable flags, `last_jiffies`, and a spinlock. `ds1553_rtc_read_time()` and `ds1553_rtc_set_time()` handle BCD calendar conversion with century support. `ds1553_rtc_update_alarm()` writes alarm registers and interrupt enable state. `ds1553_nvram_read()` and `ds1553_nvram_write()` provide byte nvmem access up to `RTC_OFFSET`.

Control flow: probe maps the resource, detects/stops the RTC stop bit, warns on battery-low, initializes cached state, registers the RTC, then optionally requests the IRQ and registers nvmem. Reads assert `RTC_READ`, sample the calendar, then deassert control. Writes assert `RTC_WRITE`, program fields, write the shared century/control register carefully, and exit write mode. Alarm setup stores requested fields in software, writes them to hardware, and enables the alarm interrupt when requested. The IRQ handler distinguishes alarm versus update-style wildcard events and calls `rtc_update_irq()`.

State and persistence: time, alarm registers, control bits, and NVRAM persist in the chip. Cached alarm fields and `irqen` are runtime mirrors used because the alarm read path reports driver state rather than re-reading all hardware semantics.

Dependencies and integration: integrates with platform MMIO resources, RTC core, nvmem, jiffies delay logic, and optional IRQs. Module alias is `platform:rtc-ds1553`.

Risks and test signals: the one-jiffy read delay avoids continuous read hazards but may be timing-sensitive. Alarm support depends on IRQ presence but the feature bit is not explicitly cleared after failed IRQ setup. Test stop-bit recovery, century register preservation, battery-low warning, wildcard/update alarm behavior, IRQ unavailable paths, and NVRAM offset coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1553.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1672.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1672.c

Purpose: implements a simple I2C RTC driver for the Dallas/Maxim DS1672, whose timekeeping is a 32-bit seconds counter plus control/trickle registers.

Important APIs/types/functions: `ds1672_read_time()` reads the control register, rejects a stopped oscillator via `DS1672_REG_CONTROL_EOSC`, reads the 4-byte little-endian counter, and converts it with `rtc_time64_to_tm()`. `ds1672_set_time()` writes the counter bytes and clears control to enable counting. `ds1672_probe()` checks raw I2C functionality, allocates the RTC, sets `range_max = U32_MAX`, registers the RTC, and stores client data.

Control flow: reads first perform a one-byte control register transaction to validate oscillator state, then perform a block-style I2C transfer from counter base. Writes send a six-byte buffer starting at counter base, containing four seconds bytes plus a zero control register byte. There is no alarm, IRQ, nvmem, or suspend/resume logic.

State and persistence: persistent state is the hardware seconds counter and control register. The driver has no private state beyond the registered `rtc_device` stored as I2C client data.

Dependencies and integration: depends on the I2C core, RTC core, and OF/I2C match tables (`dallas,ds1672`, `ds1672`). It requires `I2C_FUNC_I2C`.

Risks and test signals: the 32-bit counter limits representable time to the U32 seconds range. Setting time unconditionally clears the control register, so platform-specific trickle/control configuration is not preserved by this path. Test oscillator-stopped reads, full counter endian conversion, set/read round trips near `U32_MAX`, and adapter functionality rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1672.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1685.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1685.c

Purpose: provides a feature-rich platform driver for Dallas/Maxim DS1685/DS1687-family RTCs and related DS17x85 devices. It handles direct or indirect register access, BCD or binary time modes, alarm interrupts, extended wake/kickstart/RAM-clear events, battery and serial sysfs attributes, optional proc output, nvmem, and an exported poweroff helper.

Important APIs/types/functions: hardware access is abstracted through `struct ds1685_priv` callbacks `read`/`write`, selected between `ds1685_read()`/`ds1685_write()` and indirect variants. Core RTC methods are `ds1685_rtc_read_time()`, `ds1685_rtc_set_time()`, `ds1685_rtc_read_alarm()`, `ds1685_rtc_set_alarm()`, and `ds1685_rtc_alarm_irq_enable()`. `ds1685_rtc_begin_data_access()`/`ds1685_rtc_end_data_access()` manage SET and bank switching. `ds1685_nvram_read()`/`ds1685_nvram_write()` expose banked NVRAM. `ds1685_rtc_poweroff()` programs auxiliary-battery wake/kickstart behavior and asserts power-off.

Control flow: probe consumes platform data, maps register resources, initializes access mode and callbacks, normalizes oscillator/data mode/DST/24-hour settings, checks batteries, clears pending interrupts, enables kickstart, allocates the RTC, requests an optional threaded IRQ, adds sysfs attributes, registers nvmem, and finally registers the RTC. The IRQ handler reads control B/C, reports periodic/alarm/update events to the RTC core, or dispatches extended events for kickstart, wake alarm, and RAM clear. Removal disables standard and extended interrupts.

State and persistence: persistent state includes time, alarms, control registers, NVRAM, serial number, and power/wake configuration stored by the chip. Runtime state includes access callbacks, register step, BCD mode, IRQ number, and platform callbacks for poweroff/wake/RAM-clear handling.

Dependencies and integration: integrates with platform data from `<linux/rtc/ds1685.h>`, RTC core locks, MMIO, nvmem, procfs, sysfs attribute groups, threaded IRQs, and exported symbol users of `ds1685_rtc_poweroff()`.

Risks and test signals: bank switching and NVRAM burst mode are error-prone, and the bank0 NVRAM write loop appears to write non-time bank0 bytes to `NVRAM_BANK0_BASE` without adding `pos`. The IRQ handler returns `IRQ_NONE` for extended-only events because `events` remains zero. Test direct and indirect access, BCD/binary conversions, 12-to-24-hour migration, banked NVRAM reads/writes, no-IRQ feature clearing, extended interrupts, sysfs/proc output, and poweroff callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1685.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1742.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1742.c

Purpose: supports DS1742/DS1743-style memory-mapped RTC/NVRAM devices where the RTC occupies the last 8 bytes of a larger battery-backed memory resource.

Important APIs/types/functions: `struct rtc_plat_data` holds separate NVRAM and RTC register base pointers plus `last_jiffies`. `ds1742_rtc_read_time()` and `ds1742_rtc_set_time()` implement BCD calendar access with century/control sharing. `ds1742_nvram_read()` and `ds1742_nvram_write()` expose the non-RTC portion of the resource through nvmem.

Control flow: probe maps the single memory resource, splits it into NVRAM and RTC windows using `resource_size(res) - RTC_SIZE`, starts the RTC if the stop bit is set, warns if the battery flag is absent, initializes driver data, allocates/registers the RTC, and registers nvmem. Time reads use the read latch bit and a one-jiffy delay for back-to-back reads; writes use the write bit and preserve the century bits when exiting write mode.

State and persistence: time and NVRAM persist in the mapped chip. Runtime state is just the mapped pointer split and last-read jiffies guard.

Dependencies and integration: depends on platform MMIO resources, RTC core, BCD helpers, OF matching (`maxim,ds1742`), and nvmem.

Risks and test signals: correctness depends on a resource large enough to contain both NVRAM and the trailing RTC registers. There is no alarm support. Test resource sizing, DS1742 versus DS1743 NVRAM sizes, stop-bit recovery, battery flag warning, century conversion, and nvmem reads/writes ending before the RTC window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1742.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds2404.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds2404.c

Purpose: implements a platform RTC driver for the DS2404 elapsed-time counter using three GPIO lines to bit-bang reset, clock, and data rather than a standard bus controller.

Important APIs/types/functions: `struct ds2404` stores device and GPIO descriptors. `ds2404_reset()`, `ds2404_write_byte()`, and `ds2404_read_byte()` implement the serial protocol. `ds2404_read_memory()` and `ds2404_write_memory()` execute DS2404 memory commands, scratchpad verification, and copy-scratchpad completion. RTC methods `ds2404_read_time()` and `ds2404_set_time()` read/write the 32-bit little-endian counter.

Control flow: probe allocates state and RTC device, obtains `rst`, `clk`, and `dq` GPIOs with expected initial directions, registers the RTC, then enables the oscillator by writing control memory. Reads reset the chip, issue read-memory at counter offset `0x203`, fetch four bytes, and convert seconds to `rtc_time`. Writes program the same offset via write-scratchpad, verify by reading scratchpad contents, then copy it to memory and wait for completion.

State and persistence: counter and oscillator control persist in DS2404 hardware. The driver stores only GPIO descriptors and the device pointer at runtime.

Dependencies and integration: depends on platform GPIO descriptors, busy-wait microsecond delays, RTC core, and a `platform:ds2404` binding. `range_max` is `U32_MAX`.

Risks and test signals: `ds2404_write_memory()` busy-waits on DQ without a timeout, so a broken bus can hang. Verification failures only log and return void, so `set_time()` can report success after failed writes. Test GPIO polarity, protocol timing, oscillator enable, write verification failure, stuck DQ behavior, and U32 boundary conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds2404.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds3232.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds3232.c

Purpose: supports Maxim/Dallas DS3232 I2C and DS3234 SPI RTCs using a shared regmap-based core. It provides calendar, one-shot alarm, SRAM nvmem, optional temperature hwmon, IRQ wake support, and both I2C/SPI module registration.

Important APIs/types/functions: `struct ds3232` stores device, regmap, IRQ, RTC, and suspend state. `ds3232_probe()` is the shared core. `ds3232_read_time()`/`ds3232_set_time()` access the first seven registers, handling 12/24-hour and century bits. `ds3232_read_alarm()`/`ds3232_set_alarm()` use alarm1. `ds3232_irq()` disables alarm1, clears A1F, and reports `RTC_AF`. `ds3232_nvmem_read()`/`write()` expose SRAM; `ds3232_hwmon_read_temp()` exposes temperature.

Control flow: bus-specific probes create an I2C or SPI regmap, perform any SPI control setup, and call the shared probe. The shared probe clears oscillator/alarm status, configures interrupt mode, enables wake capability when IRQ exists, registers hwmon, registers the RTC, registers SRAM nvmem, and requests a threaded IRQ if available. Suspend/resume toggles IRQ wake for I2C devices.

State and persistence: time, alarm registers, SRAM, oscillator flags, control bits, and temperature conversion state are hardware-backed. Runtime state tracks regmap and IRQ availability.

Dependencies and integration: integrates with I2C, SPI, regmap, RTC, nvmem, hwmon, OF/I2C/SPI IDs, and PM sleep hooks.

Risks and test signals: the alarm path only supports alarm1 and disables it after interrupt, so repeated alarms require reprogramming. SPI probe overwrites parts of control/status during setup. Test I2C and SPI registration combinations, oscillator-stop warnings, alarm IRQ clear/disable, SRAM nvmem range, hwmon conversion including negative temperatures, wake suspend/resume, and no-IRQ alarm behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds3232.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-efi.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-efi.c

Purpose: exposes EFI firmware time services as a Linux RTC device on EFI-based systems. It supports read, set, and procfs capability reporting but no alarm.

Important APIs/types/functions: `convert_to_efi_time()` maps `struct rtc_time` to `efi_time_t`; `convert_from_efi_time()` validates and converts EFI fields back to RTC time. `compute_yday()` and `compute_wday()` fill derived fields. `efi_read_time()` calls `efi.get_time()`, while `efi_set_time()` calls `efi.set_time()`. `efi_procfs()` prints current EFI time and capability data.

Control flow: the platform probe first checks `efi.get_time()` works, allocates an RTC, clears `RTC_FEATURE_ALARM`, marks the device wake-capable, and registers it. Reads validate each EFI field range before returning to the RTC core. Writes always use unspecified timezone and map `tm_isdst` to EFI daylight flags.

State and persistence: persistent state lives entirely in EFI firmware/underlying platform RTC. The driver maintains no private state beyond the registered RTC.

Dependencies and integration: depends on global EFI runtime service pointers, platform driver probe, RTC core, and proc support through `rtc_class_ops.proc`.

Risks and test signals: firmware implementations vary; invalid EFI fields produce `-EIO`, and runtime-service failures map to `-EINVAL`. Timezone is not preserved on writes. Test usable/unusable EFI service paths, invalid firmware field rejection, DST flag mapping, proc capability output, and absence of alarm features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-efi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-em3027.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-em3027.c

Purpose: provides a minimal I2C RTC driver for the EM Microelectronic EM3027, covering only calendar read/write operations.

Important APIs/types/functions: `em3027_get_time()` reads seven watch registers starting at `EM3027_REG_WATCH_SEC` and converts BCD fields. `em3027_set_time()` writes the same watch register block from `struct rtc_time`. `em3027_probe()` checks `I2C_FUNC_I2C` and registers the RTC with `em3027_rtc_ops`.

Control flow: reads issue a two-message I2C transaction: write the starting register address, then read the seven time/date bytes. Writes send an eight-byte I2C message containing the start register followed by BCD second, minute, hour, day, weekday, month, and year. Probe does not initialize control, alarm, or status registers.

State and persistence: the hardware stores time/date. The driver stores only the `rtc_device` in client data and has no private cache.

Dependencies and integration: depends on I2C, RTC core, BCD helpers, and optional OF matching (`emmicro,em3027`).

Risks and test signals: years are assumed to be 2000-2099 via `+100` and `% 100`; alarm registers are defined but unused. No invalid-clock/status checks are performed. Test block read/write transactions, year boundary handling, adapter functionality rejection, and behavior after battery loss or invalid register contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-em3027.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ep93xx.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ep93xx.c

Purpose: supports the RTC block embedded in Cirrus Logic EP93xx processors. It exposes a seconds counter as the RTC and reports software compensation fields via procfs and sysfs.

Important APIs/types/functions: `struct ep93xx_rtc` stores the mapped MMIO base. `ep93xx_rtc_read_time()` reads `EP93XX_RTC_DATA`; `ep93xx_rtc_set_time()` writes seconds plus one to `EP93XX_RTC_LOAD`. `ep93xx_rtc_get_swcomp()` decodes preload/delete fields from `EP93XX_RTC_SWCOMP`. Sysfs attributes `comp_preload` and `comp_delete` expose compensation data.

Control flow: probe allocates state, maps the resource, allocates an RTC, attaches `ep93xx_rtc_ops`, sets `range_max = U32_MAX`, adds the sysfs group, and registers the device. There is no IRQ or alarm flow despite match/control registers existing in the hardware definition.

State and persistence: the hardware counter and compensation register are SoC state. Runtime state is just the MMIO base.

Dependencies and integration: integrates with platform/OF matching (`cirrus,ep9301-rtc`), MMIO, RTC core, procfs, and sysfs attribute groups.

Risks and test signals: `set_time()` writes `secs + 1`, so tests must verify this matches hardware load semantics and does not introduce off-by-one behavior. Alarm registers are unused. Test read/set round trips, compensation decoding, sysfs group registration failure, and U32 range boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ep93xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-fm3130.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-fm3130.c

Purpose: implements an I2C RTC driver for the Ramtron FM3130, including clock read/write, alarm register access, alarm enable control, and probe-time cleanup of oscillator/read/write/calibration modes.

Important APIs/types/functions: `struct fm3130` caches register buffers, I2C messages, RTC pointer, and validity flags. `fm3130_rtc_mode()` toggles read/write mode bits. `fm3130_get_time()`/`fm3130_set_time()` access clock registers. `fm3130_read_alarm()`/`fm3130_set_alarm()` handle alarm registers with `0x80` wildcard/disable values. `fm3130_alarm_irq_enable()` toggles `AEN`.

Control flow: probe validates I2C functionality, builds reusable I2C messages, reads time and alarm blocks, clears calibration/read/write modes, starts the oscillator, clears low-battery/POR flags, configures alarm write-protect control, sanity-checks cached clock/alarm values, and registers the RTC even if cached values are invalid. Time reads enter read mode, perform a block transfer, exit normal mode, and decode BCD. Time writes enter write mode and write individual bytes. Alarm writes update five alarm registers and control bits.

State and persistence: time, alarm, control, and calibration registers persist in the chip. Runtime `data_valid` and `alarm_valid` determine whether reads return `-EIO` until a successful write establishes sane data.

Dependencies and integration: depends on I2C/SMBus byte writes, RTC core, BCD helpers, and client ID binding.

Risks and test signals: probe labels the clock-register sanity block as alarm validation first, so alarm validity appears based on current clock fields rather than alarm fields. I2C SMBus writes in loops do not check every return. Test invalid battery/POR data, mode cleanup, oscillator enable, alarm wildcard handling, alarm enable/disable, and partial I2C failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-fm3130.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-fsl-ftm-alarm.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-fsl-ftm-alarm.c

Purpose: presents NXP/Freescale FlexTimer Module hardware as an RTC alarm device. It is not a battery-backed wall-clock RTC; it uses system time for `read_time()` and the FTM counter for short wake alarms.

Important APIs/types/functions: `struct ftm_rtc` stores RTC device, MMIO base, endian mode, and alarm frequency. `rtc_readl()`/`rtc_writel()` abstract endian access. `ftm_clean_alarm()`, `ftm_counter_enable()`, `ftm_irq_enable()`, and `ftm_irq_acknowledge()` manage FTM counter state. RTC methods are `ftm_rtc_read_time()`, `ftm_rtc_set_alarm()`, `ftm_rtc_read_alarm()`, and `ftm_rtc_alarm_irq_enable()`.

Control flow: probe maps registers, requests the IRQ, detects `big-endian`, computes the 250 Hz alarm frequency, initializes wake IRQ support, and registers the RTC. Setting an alarm clears any existing counter, computes cycles from requested alarm time minus `ktime_get_real_seconds()`, rejects values above 0xffff cycles, writes `MOD = cycle - 1`, enables the counter, and enables interrupts. The IRQ handler reports `RTC_AF`, acknowledges TOF with an erratum workaround, disables IRQs, and cleans the alarm.

State and persistence: there is no persistent RTC time. Alarm state lives in volatile FTM registers; runtime state stores register base and derived frequency.

Dependencies and integration: uses platform/OF/ACPI matching, MMIO, RTC core, wake IRQ helpers, and Freescale FTM register definitions.

Risks and test signals: negative or zero alarm deltas can underflow `cycle`, and max alarm range is only about 262 seconds. `read_alarm()` is a stub. Test endian modes, out-of-range and past alarms, TOF clear workaround, wake IRQ setup failure, and suspend wake behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-fsl-ftm-alarm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ftrtc010.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ftrtc010.c

Purpose: supports the Faraday FTRTC010/Gemini SoC RTC, including a workaround for hardware that cannot directly store full absolute time. The driver derives current time from hardware day/hour/min/sec counters plus a software offset register.

Important APIs/types/functions: `struct ftrtc010_rtc` stores MMIO base, IRQ, and PCLK/EXTCLK handles. `ftrtc010_rtc_read_time()` reads counters and `FTRTC010_RTC_RECORD` offset. `ftrtc010_rtc_set_time()` computes and writes a new offset and triggers control register bit `0x01`. `ftrtc010_rtc_probe()` enables clocks, maps MMIO, computes RTC range from current counters, requests IRQ, and registers the RTC.

Control flow: probe enables optional clocks with explicit unwind, obtains IRQ and memory resource, maps registers, allocates the RTC, samples the current counter baseline to set `range_min`/`range_max`, requests a shared IRQ, then registers the RTC. The IRQ handler currently acknowledges nothing and always returns handled.

State and persistence: persistent time is represented by hardware counters plus the offset record register. Runtime state includes clocks and the mapped base. The clocks are disabled on remove or probe failure.

Dependencies and integration: depends on platform/OF matching (`cortina,gemini-rtc`, `faraday,ftrtc010`), clk framework, MMIO, IRQ, and RTC core.

Risks and test signals: the IRQ handler is a stub, so alarm/interrupt behavior is not implemented. `devm_clk_get()` failures are logged but treated as optional; cleanup checks `IS_ERR`. Test clock enable/unwind, offset math after long uptime, range calculations, IRQ request, remove cleanup, and read/set round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ftrtc010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-gamecube.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-gamecube.c

Purpose: supports the RTC/SRAM portion of Nintendo GameCube, Wii, and Wii U MX23L4005 hardware over the EXI bus. The hardware counter is combined with a platform bias value stored in SRAM to produce Unix time.

Important APIs/types/functions: `struct priv` stores regmap, EXI MMIO base, and `rtc_bias`. `exi_read()`/`exi_write()` implement 24-bit register access over EXI immediate transfers. `gamecube_rtc_read_time()` adds counter plus bias; `gamecube_rtc_set_time()` writes timestamp minus bias. `gamecube_rtc_ioctl()` implements `RTC_VL_READ`. `gamecube_rtc_read_offset_from_sram()` unlocks SRAM access on Wii/Wii U style systems and reads `RTC_SRAM_BIAS`.

Control flow: probe maps EXI registers, creates a custom regmap bus, reads the RTC bias from SRAM, allocates the RTC, sets the U32 range, and registers it. EXI operations select device 1, send register address, spin until transfer completion, read/write data, then clear channel parameters. Voltage-low ioctl reads control flags and reports invalid/low-backup state.

State and persistence: RTC counter and SRAM bias persist in console hardware. The driver caches `rtc_bias` because it may not be persistently writable on all supported consoles.

Dependencies and integration: depends on platform/OF matching for `nintendo,latte-exi`, `hollywood-exi`, and `flipper-exi`, OF address lookup for SRAM protection registers, regmap, MMIO big-endian access, and RTC core.

Risks and test signals: the driver assumes no other EXI bus users and directly manipulates SRAM protection. `devm_rtc_register_device()` return is ignored. Test bias read on GameCube/Wii/Wii U paths, voltage-low ioctl, regmap access table enforcement, EXI timeout assumptions, and set/read with nonzero bias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-gamecube.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-generic.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-generic.c

Purpose: is a small platform wrapper that registers an RTC using `rtc_class_ops` supplied as platform data. It lets architecture or board code provide the actual RTC operations while reusing RTC class registration.

Important APIs/types/functions: `generic_rtc_probe()` obtains `const struct rtc_class_ops *ops` with `dev_get_platdata()`, registers a device named `rtc-generic` via `devm_rtc_device_register()`, and stores the returned RTC in platform driver data.

Control flow: `module_platform_driver_probe()` registers a probe-only platform driver named `rtc-generic`. Probe does no resource mapping and no validation beyond checking the returned RTC pointer.

State and persistence: this file owns no hardware or persistent state. All RTC state and behavior are delegated to platform-provided operations.

Dependencies and integration: depends on platform bus users passing a valid ops table, RTC core, and module alias `platform:rtc-generic`.

Risks and test signals: invalid or missing platform data would pass a NULL ops pointer into RTC registration depending on core validation. There is no OF/ACPI matching. Test platform-data registration, ops lifetime, read/set behavior provided by board code, and module unload/devres cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-goldfish.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-goldfish.c

Purpose: implements the Android Goldfish emulator RTC using memory-mapped goldfish timer registers for wall-clock time and alarm interrupts.

Important APIs/types/functions: `struct goldfish_rtc` stores MMIO base, IRQ, and RTC pointer. `goldfish_rtc_read_time()`/`goldfish_rtc_set_time()` convert between nanosecond hardware registers and seconds-based `rtc_time`. `goldfish_rtc_read_alarm()`, `goldfish_rtc_set_alarm()`, and `goldfish_rtc_alarm_irq_enable()` manage timer alarm registers. `goldfish_rtc_interrupt()` clears the interrupt and reports `RTC_AF`.

Control flow: probe allocates state, maps the MMIO resource, obtains IRQ, allocates RTC, sets `range_max = U64_MAX / NSEC_PER_SEC`, requests the IRQ, and registers the RTC. Alarm setting writes high then low nanosecond fields and enables IRQs; disabling clears an active alarm if the status register indicates one. Reads combine high/low registers and divide by nanoseconds per second.

State and persistence: state is emulator-provided timer/RTC register content. Runtime state is base pointer, IRQ, and RTC object.

Dependencies and integration: depends on platform/OF binding `google,goldfish-rtc`, goldfish MMIO accessors, RTC core, and timer register definitions.

Risks and test signals: high/low 64-bit register reads are not latched in the driver, so rollover between reads is a potential concern if hardware does not guarantee coherence. Test alarm enable/disable, interrupt clear, high/low rollover, no-IRQ probe failure, and large timestamp range handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-goldfish.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-hid-sensor-time.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-hid-sensor-time.c

Purpose: exposes a HID Sensor Hub time sensor as a read-only RTC. It obtains date/time fields from HID input reports rather than from direct RTC registers.

Important APIs/types/functions: `struct hid_time_state` stores sensor callbacks, common HID attributes, per-field attribute info, buffers, completion, spinlock, and RTC pointer. `hid_time_parse_report()` validates all six time attributes share a report and have acceptable sizes/units. `hid_time_capture_sample()` fills `time_buf`; `hid_time_proc_event()` publishes it to `last_time` and completes waiting readers. `hid_rtc_read_time()` triggers a synchronous report request and waits up to six seconds.

Control flow: probe parses common attributes and the time report, registers callbacks, opens the sensor hub, starts HID I/O early, registers the RTC, and unwinds callback/device state on failure. Reads reinitialize completion, request one raw value to cause the full report to arrive, wait for the event callback, then copy the last completed time under spinlock. Remove closes the hub and unregisters callbacks.

State and persistence: no persistent state is stored by this driver. Runtime state is the latest HID report and synchronization primitives.

Dependencies and integration: depends on HID sensor hub APIs, IIO HID namespace, platform device IDs (`HID-SENSOR-2000a0`), RTC core, completions, and spinlocks.

Risks and test signals: the RTC is read-only and depends on HID report timing. Invalid raw lengths become all-ones values that may later fail RTC validation elsewhere. Test report attribute validation, 8/16/32-bit year handling, timeout and signal interruption, callback ordering, remove while reads are pending, and registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-hid-sensor-time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-hym8563.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-hym8563.c

Purpose: supports the Haoyu HYM8563 I2C RTC, including calendar read/write, minute-resolution alarms, optional interrupt wakeup, and optional common-clock output registration.

Important APIs/types/functions: `struct hym8563` stores the I2C client, RTC, and optional `clk_hw`. RTC methods include `hym8563_rtc_read_time()`, `hym8563_rtc_set_time()`, `hym8563_rtc_read_alarm()`, `hym8563_rtc_set_alarm()`, and `hym8563_rtc_alarm_irq_enable()`. `hym8563_init_device()` clears STOP, disables timer/alarm interrupts, and clears flags. Clock-out support is implemented through `hym8563_clkout_ops`.

Control flow: probe allocates the RTC, initializes the chip, requests a threaded low-level IRQ when present, enables wakeup if IRQ or `wakeup-source` exists, checks the validity bit, sets feature flags, optionally registers clkout, and registers the RTC. Setting time stops the clock, writes seven BCD registers, then restarts it. Alarm setup disables AIE, writes minute/hour/day/weekday alarm bytes with disable bits for wildcard fields, then restores requested enable state. IRQ clears the alarm flag under `rtc_lock()`.

State and persistence: time, alarm, validity flag, control bits, and clkout configuration persist in chip registers. Runtime state holds client/RTC/clkout wrapper.

Dependencies and integration: uses I2C SMBus block/byte operations, RTC core, common clock framework when enabled, OF matching (`haoyu,hym8563`), and PM sleep IRQ wake hooks.

Risks and test signals: century is intentionally ignored, limiting range to 2000-2099. The IRQ handler clears AF but does not call `rtc_update_irq()`, so alarm notification depends on RTC core polling/level behavior rather than explicit event reporting. Test invalid-clock reads, minute alarm semantics, wake suspend/resume, clkout rates/enable, no-IRQ feature behavior, and STOP handling on failed writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-hym8563.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-imx-sc.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-imx-sc.c

Purpose: exposes the NXP i.MX System Controller RTC as a Linux RTC using SCU RPC for reads/alarms and an ARM SMCCC SMC call for setting time.

Important APIs/types/functions: global `rtc_ipc_handle` and `imx_sc_rtc` hold the SCU handle and RTC device. `imx_sc_rtc_read_time()` sends `IMX_SC_TIMER_FUNC_GET_RTC_SEC1970`. `imx_sc_rtc_set_time()` packs calendar fields into SMC arguments for `IMX_SIP_SRTC_SET_TIME`. `imx_sc_rtc_set_alarm()` sends `IMX_SC_TIMER_FUNC_SET_RTC_ALARM` then toggles SCU IRQ enable. `imx_sc_rtc_alarm_notify()` maps SCU RTC notifications to `rtc_update_irq()`.

Control flow: probe obtains the SCU IPC handle, marks wake-capable, allocates/registers the RTC, then registers an SCU IRQ notifier. Alarm enable calls `imx_scu_irq_group_enable()` for RTC group/bit. Notification ignores non-RTC events and reports alarm events.

State and persistence: time and alarm state are owned by system controller firmware. Driver state is global, implying single-instance design.

Dependencies and integration: depends on i.MX SCU firmware APIs, ARM SMCCC, device tree match `fsl,imx8qxp-sc-rtc`, RTC core, and SCU IRQ notifier infrastructure.

Risks and test signals: notifier registration is not devm-managed in this file, and global state limits multi-instance safety. `set_time()` returns firmware `res.a0` directly. Test SCU handle failure, SMC error propagation, alarm enable/disable, notification filtering, wake capability, and U32 range boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-imx-sc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-imx-sm-bbm.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-imx-sm-bbm.c

Purpose: provides an RTC driver for the i.MX System Manager BBM service through the SCMI i.MX BBM protocol. It supports time read/write, alarm programming, and SCMI event notification.

Important APIs/types/functions: `struct scmi_imx_bbm` stores protocol ops, RTC device, protocol handle, and notifier block. `scmi_imx_bbm_read_time()`/`set_time()` call `rtc_time_get()` and `rtc_time_set()`. `scmi_imx_bbm_set_alarm()` calls `rtc_alarm_set()` with enable=true and the alarm timestamp. `scmi_imx_bbm_alarm_irq_enable()` only handles disable by calling `rtc_alarm_set(..., false, 0)`. `scmi_imx_bbm_rtc_notifier()` reports RTC BBM events.

Control flow: SCMI probe obtains protocol operations, enables wake capability, stores driver data, allocates the RTC, registers an SCMI event notifier for `SCMI_EVENT_IMX_BBM_RTC`, and registers the RTC. Alarm events are delivered asynchronously through SCMI notifications.

State and persistence: RTC time and alarm persist in the BBM/System Manager firmware domain. Runtime state is the SCMI protocol binding and notifier.

Dependencies and integration: depends on SCMI core, i.MX SCMI BBM protocol headers, RTC core, and `module_scmi_driver()` with protocol ID matching.

Risks and test signals: alarm enable ignores `enable=1` unless an alarm is set, which is intentional but different from drivers that toggle an existing alarm. Unexpected non-RTC BBM events are logged. Test protocol-get failure, notifier registration, alarm disable path, event delivery, wake setup rollback on init failure, and U32 range behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-imx-sm-bbm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-imxdi.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-imxdi.c

Purpose: implements the Freescale/NXP i.MX DryIce RTC using a security/tamper-aware 47-bit 32 kHz counter truncated to seconds. It handles complex DryIce valid, non-valid, and failure states, synchronized low-power-domain writes, alarms, wake IRQs, and security-violation reporting.

Important APIs/types/functions: `struct imxdi_dev` stores platform device, RTC, MMIO, clock, cached DSR bits, interrupt lock, write waitqueue, write mutex, and alarm work. State handlers `di_handle_state()`, `di_handle_invalid_state()`, `di_handle_failure_state()`, and `di_handle_invalid_and_failure_state()` recover or reject DryIce states. `di_write_wait()` serializes register writes and waits for write-complete/error IRQs. RTC methods are `dryice_rtc_read_time()`, `dryice_rtc_set_time()`, `dryice_rtc_read_alarm()`, `dryice_rtc_set_alarm()`, and `dryice_rtc_alarm_irq_enable()`.

Control flow: probe maps registers, obtains normal and optional security IRQs, enables the input clock, masks interrupts, runs DryIce state recovery, requests IRQs, enables wake IRQ, attaches RTC ops, and registers the RTC. Register writes use write-complete interrupts and a waitqueue. The IRQ handler handles security violations, write completion/error wakeups, and alarm flags. Alarm work clears `DSR_CAF` in sleepable context before reporting `RTC_AF`.

State and persistence: DryIce stores time, alarm, tamper/security state, monotonic configuration, and lock bits in hardware. Runtime state tracks synchronization and work for writes/alarms.

Dependencies and integration: depends on platform/OF match `fsl,imx25-rtc`, clk framework, MMIO, IRQs, workqueues, wake IRQ helpers, RTC core locks, and DryIce security semantics.

Risks and test signals: reading DSR clears WCF, so paths must avoid disrupting write completion; this is carefully guarded in alarm read but remains a central risk. Some failure states require main or battery power cycling and return `-ENODEV`. Test each DryIce state transition, write timeout/error handling, concurrent alarm/write paths, optional security IRQ absence, wake IRQ setup, clock cleanup, and alarm work flushing on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-imxdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl12022.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl12022.c

Purpose: supports the Intersil/Renesas ISL12022 I2C RTC with calendar, alarm, battery voltage reporting, optional IRQ, fixed 32 kHz clock output, and hwmon temperature exposure.

Important APIs/types/functions: `struct isl12022` stores RTC, regmap, IRQ, and IRQ-enabled state. `isl12022_rtc_read_time()`/`set_time()` use regmap bulk operations and write-enable bit `WRTC`. `isl12022_rtc_read_alarm()`/`set_alarm()` program six alarm registers whose MSBs enable matching. `isl12022_rtc_ioctl()` implements `RTC_VL_READ`. `isl12022_register_clock()`, `isl12022_set_trip_levels()`, and `isl12022_hwmon_register()` integrate clock, battery thresholds, and temperature.

Control flow: probe validates I2C, creates regmap, registers/possibly disables clock output, configures battery trip thresholds, registers hwmon, allocates RTC, sets 2000-2099 range, configures IRQ if present, and registers the RTC. Alarm setup disables past alarms, writes a temporary nonmatching weekday to avoid false matches, then bulk-writes all alarm fields. IRQ reads SR, reports alarm events, and relies on configured automatic reset/single-event mode.

State and persistence: time, alarm, temperature, status, battery thresholds, and clock output are chip state. `irq_enabled` mirrors Linux IRQ masking.

Dependencies and integration: depends on I2C, regmap, RTC, hwmon, common clock, OF properties (`#clock-cells`, `isil,battery-trip-levels-microvolt`), and threaded IRQs.

Risks and test signals: `alarm_irq_enable()` masks/unmasks the Linux IRQ rather than changing chip alarm bits; setup initially leaves IRQ enabled. Temperature conversion uses raw 10-bit half-Kelvin units from little-endian registers. Test past/future alarm programming, IRQ masking, voltage ioctl, trip-level mapping, F_OUT behavior with/without clock provider, hwmon enable failure, and 2000/2099 range limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl12022.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl12026.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl12026.c

Purpose: supports the Intersil ISL12026 I2C RTC and its separate EEPROM array exposed through nvmem at companion I2C address `0x57`.

Important APIs/types/functions: `struct isl12026` stores RTC and dummy EEPROM client. `isl12026_arm_write()`/`isl12026_disarm_write()` implement the WEL/RWEL write-enable sequence. `isl12026_rtc_read_time()` and `isl12026_rtc_set_time()` access CCR registers with BCD conversion and century field. `isl12026_nvm_read()`/`isl12026_nvm_write()` expose 512 bytes of EEPROM with page-sized writes. `isl12026_force_power_modes()` applies optional `isil,pwr-bsw` and `isil,pwr-sbib` properties.

Control flow: probe checks I2C functionality, allocates state, optionally updates power mode bits, creates the dummy EEPROM client, allocates RTC, registers nvmem, and registers RTC. Time writes arm register writes, write the clock block, then disarm. Nvmem writes split data at 16-byte page boundaries and sleep for EEPROM write time after each page.

State and persistence: time registers, power mode bits, and EEPROM contents persist in hardware. Runtime state includes the dummy nvmem client and RTC pointer.

Dependencies and integration: depends on I2C transfers with two-byte register addresses, RTC core, nvmem provider, OF properties, and dummy I2C client lifecycle.

Risks and test signals: if RTC registration fails after the dummy client is created, devm cleanup will not automatically unregister it because only `remove()` does that for a bound device. Error paths after dummy creation deserve review. Test write-enable sequencing, oscillator/RTC failure warnings, 12/24-hour read conversion, page boundary nvmem writes, power property updates, and dummy-client cleanup on failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl12026.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl1208.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl1208.c

Purpose: supports the ISL1208 family, including ISL1208/1209/1218/1219 and RAA215300 A0 variants. It provides RTC time, alarms, proc/sysfs trim and user data, small nvmem, tamper/event detection, timestamp reporting for ISL1219, and oscillator input selection.

Important APIs/types/functions: `struct isl1208_config` describes per-chip nvmem length, tamper, timestamp, and inverted oscillator bit quirks. `struct isl1208_state` stores RTC, config, and nvmem config. Low-level helpers `isl1208_i2c_read_regs()`/`isl1208_i2c_set_regs()` wrap SMBus block transfers. RTC operations call `isl1208_i2c_read_time()`, `isl1208_i2c_set_time()`, `isl1208_i2c_read_alarm()`, and `isl1208_i2c_set_alarm()`. `isl1208_rtc_interrupt()` handles alarm and tamper events. Sysfs exposes `atrim`, `dtrim`, `usr`, and optional `timestamp0`.

Control flow: probe validates reserved bits, selects config from match data, detects optional `xin`/`clkin` clocks and oscillator bit polarity, allocates RTC, reads status, configures oscillator, warns on power failure, enables tamper detection if supported, adds timestamp and trim/user sysfs groups, requests alarm and optional event IRQs, registers nvmem, and registers the RTC. Alarm IRQ handling works around delayed/NAK-prone status reads, reports alarm events, disables and clears ALM, and notifies timestamp sysfs on tamper.

State and persistence: time, alarm, trim registers, user bytes, tamper status, and timestamp registers are chip state. Runtime config selects feature exposure and nvmem size.

Dependencies and integration: depends on I2C/SMBus, RTC, nvmem, OF IRQ lookup, optional clocks, sysfs, procfs, and device/OF match data.

Risks and test signals: interrupt handler return paths can return negative I2C errors as `irqreturn_t` values in some failure cases. IRQ wake is enabled without a matching explicit disable path. Test each chip config, oscillator input selection including inverted bit, RTCF warning, alarm delayed-clear behavior, tamper/timestamp sysfs notification, nvmem sizes, trim decoding, and reserved-bit validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl1208.c -->
