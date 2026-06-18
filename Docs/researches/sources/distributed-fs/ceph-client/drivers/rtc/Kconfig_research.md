# sources/distributed-fs/ceph-client/drivers/rtc/Kconfig

Purpose: Kconfig menu for the Linux RTC subsystem and its chip/platform drivers. It defines core RTC library/class features, user interfaces, clock synchronization policy, optional tests/NVMEM, and hundreds of transport- or SoC-specific RTC driver symbols.

Important APIs, types, and functions: this is declarative Kconfig rather than C. Key symbols are `RTC_LIB`, `RTC_MC146818_LIB`, `RTC_CLASS`, `RTC_HCTOSYS`, `RTC_HCTOSYS_DEVICE`, `RTC_SYSTOHC`, `RTC_SYSTOHC_DEVICE`, `RTC_DEBUG`, `RTC_LIB_KUNIT_TEST`, `RTC_NVMEM`, `RTC_INTF_SYSFS`, `RTC_INTF_PROC`, `RTC_INTF_DEV`, and `RTC_INTF_DEV_UIE_EMUL`. Driver symbols follow `RTC_DRV_*` naming and are grouped mainly under I2C, SPI, shared I2C/SPI, legacy/platform, SoC, and special firmware/EC sections.

Control flow: selecting `RTC_CLASS` enables the core menu and selects `RTC_LIB`. Interface symbols default to `RTC_CLASS`, so sysfs/proc/dev support normally follows the class unless disabled. `RTC_HCTOSYS_DEVICE` and `RTC_SYSTOHC_DEVICE` choose the RTC device name used for system-clock initialization/resume and periodic NTP-to-hardware-clock synchronization. Individual driver entries set dependencies (`depends on I2C`, `SPI_MASTER`, `MFD_*`, architecture symbols, `COMPILE_TEST`) and select helper subsystems such as `REGMAP_I2C`, `WATCHDOG_CORE`, `NVMEM`, or `HWMON`.

State and persistence: Kconfig output persists in the kernel `.config` and controls which objects are compiled into vmlinux or modules. It does not store runtime state, but choices directly affect RTC class behavior and which hardware can register.

Dependencies and integration points: feeds `drivers/rtc/Makefile`, RTC core C files, per-chip drivers, KUnit, NVMEM, watchdog, hwmon, MFD, I2C, SPI, platform, architecture, and firmware interfaces. It also controls user ABI availability for `/sys/class/rtc`, `/proc/driver/rtc`, and `/dev/rtcN`.

Risks: defaulting `RTC_HCTOSYS` and `RTC_SYSTOHC` to yes can affect system time if the chosen RTC is not battery-backed or not UTC. Driver dependencies must stay aligned with actual source includes and bus APIs. Shared chips with watchdog/hwmon features can silently select extra subsystems. Menu sprawl makes duplicate or stale driver entries easy to introduce.

Test signals: run Kconfig olddefconfig/allmodconfig/randconfig, verify selected objects match Makefile mappings, check `RTC_CLASS=n` hides drivers, validate interface combinations, exercise KUnit via `RTC_LIB_KUNIT_TEST`, and boot configs with different `RTC_HCTOSYS_DEVICE`/`RTC_SYSTOHC_DEVICE` values.
