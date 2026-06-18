
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/time.c

Purpose: supplies PowerMac time initialization, RTC access, and decrementer calibration. It bridges machine-controller-specific RTC implementations and corrects timebase frequency on older 32-bit machines.

Important APIs/functions: `pmac_time_init()` reads GMT offset and DST flags from XPRAM on 32-bit NVRAM-enabled builds. `pmac_get_boot_time()`, `pmac_get_rtc_time()`, and `pmac_set_rtc_time()` dispatch to CUDA, PMU, or SMU RTC functions according to `sys_ctrler`. `pmac_calibrate_decr()` starts with generic Open Firmware calibration and optionally invokes `via_calibrate_decr()`.

Control flow: early init reads timezone metadata and returns a delta. RTC calls switch over `sys_ctrler` and return zero or `-ENODEV` when no controller backend exists. `via_calibrate_decr()` maps a VIA device found in the device tree, configures VIA timer 1 in continuous mode, measures decrementer ticks across a known timer interval, updates `ppc_tb_freq`, and unmaps the device. `pmac_calibrate_decr()` avoids VIA calibration for MacRISC2/3/4 except for the PowerMac3,5 QuickSilver special case.

State and persistence: writes only kernel globals such as `ppc_tb_freq`; reads XPRAM/NVRAM, RTC, and device-tree resources. It does not persist new values.

Dependencies and integration points: depends on CUDA, PMU, SMU, RTC conversion helpers, Open Firmware address translation, early ioremap, PowerMac machine controller selection, and generic PowerPC time/decrementer infrastructure.

Risks: VIA calibration busy-waits on hardware interrupt flags during early boot; missing or inaccurate device-tree resources make it fall back to generic calibration. RTC dispatch depends on `sys_ctrler` being correctly initialized. Older firmware quirks mean removing the QuickSilver override can regress clock accuracy.

Test signals: boot logs showing XPRAM GMT delta and stable decrementer frequency, RTC read/set on CUDA/PMU/SMU systems, suspend/resume RTC access, and time drift checks on older non-MacRISC2 PowerMacs.
