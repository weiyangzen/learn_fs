# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/backlight.h

Purpose: declares the PowerMac/PowerBook backlight control interface shared with platform implementation code.

Important APIs/types/functions: exports `pmac_backlight`, `pmac_backlight_mutex`, `pmac_has_backlight_type()`, `pmac_backlight_key()`, `pmac_backlight_key_up()`, `pmac_backlight_key_down()`, legacy PMU brightness setters/getter, and enable/disable helpers.

Control flow: inline key helpers call `pmac_backlight_key(0)` for up and `pmac_backlight_key(1)` for down. Other operations are implemented in platform code.

State and persistence: global backlight state is represented by the external `backlight_device` pointer and mutex. Hardware brightness persists according to the device/PMU state, not this header.

Dependencies and integration points: depends on the Linux backlight class and PowerMac platform backlight implementation. It integrates keyboard brightness events, legacy PMU control, and display power management.

Risks: callers must observe the locking rules from the implementation file. Legacy PMU brightness APIs may not map to all backlight hardware types.

Test signals: PowerBook/PowerMac boot tests with keyboard brightness keys, suspend/resume display tests, and lockdep checks around `pmac_backlight_mutex`.
