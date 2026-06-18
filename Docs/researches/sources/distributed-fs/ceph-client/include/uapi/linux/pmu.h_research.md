<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pmu.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pmu.h

Purpose: defines the `/dev/pmu` ABI for Apple PowerBook Power Management Unit commands, model identifiers, wake events, I2C modes, interrupt bits, and ioctls.

Important APIs and types: command constants cover power control, ADB, XPRAM/NVRAM, RTC, backlight, PC-card eject, battery state, interrupt masks, shutdown/sleep/reset, I2C, and version reads. Model enums identify OHare, Heathrow, Paddington, KeyLargo, and deprecated 68K PMUs. `PMU_IOC_*` ioctls provide sleep, backlight get/set/grab, model query, ADB availability, and sleep capability.

Control flow: userspace or platform code issues ioctls or low-level PMU commands; the PMU microcontroller updates power, backlight, battery, RTC, and wake-event state and returns status through the character device.

State and persistence: state resides in PMU firmware/hardware: power rails, wake masks, RTC/NVRAM/XPRAM, battery and lid status. Some values persist in NVRAM/RTC; most ioctl state is transient hardware state.

Dependencies and integration points: includes ioctl definitions and integrates with PowerPC platform PMU drivers, ADB, battery/power subsystems, RTC, backlight, and legacy laptop userspace tools.

Risks and test signals: risks include legacy model differences, privileged power-control misuse, size_t ioctl type compatibility, and unclear command support per PMU generation. Test compile on relevant PowerPC configs, ioctl behavior on supported hardware/emulation, backlight bounds, sleep capability gating, and PMU interrupt/wake events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pmu.h -->
