# sources/distributed-fs/ceph-client/include/linux/power/power_on_reason.h

Purpose: centralizes standard string labels for reporting a platform power-on or reset reason.

Important APIs and types: string macros cover regular power-up, RTC wakeup, watchdog timeout, software reset, reset button, CPU clock failure, crystal oscillator failure, brown-out reset, and unknown reason.

Control flow: platform or PMIC drivers select one of these constants when exposing power-on reason through logs, sysfs, debugfs, or power/reset reporting code.

State and persistence: no state is stored. The actual reset reason is hardware/platform state read by drivers.

Dependencies and integration points: standalone header intended to keep power-on reason wording consistent across drivers.

Risks and test signals: risks are mismatched labels, missing platform-specific reasons, and userspace depending on exact strings. Test reason decoding paths, fallback to unknown, and ABI expectations for exposed strings.
