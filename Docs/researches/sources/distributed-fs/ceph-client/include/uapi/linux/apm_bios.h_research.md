<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/apm_bios.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/apm_bios.h

## Purpose
Defines the legacy Advanced Power Management BIOS userspace/kernel interface, including BIOS info, power states, events, error codes, device ids, capability flags, and standby/suspend ioctls.

## Important APIs, Types, And Functions
Exports `apm_event_t`, `apm_eventinfo_t`, `struct apm_bios_info`, `APM_STATE_*`, event constants such as standby/suspend/resume/low-battery, error constants, device id masks, battery count, capability flags, `APM_IOC_STANDBY`, and `APM_IOC_SUSPEND`.

## Control Flow
Userspace queries or receives APM events through legacy APM device support and can request system standby or suspend through ioctls. Kernel/BIOS code maps requests to firmware calls and reports events/status.

## State And Persistence
Power state is system/device firmware state. BIOS segment information describes real-mode/16-bit/32-bit APM entry points and is static after boot.

## Dependencies And Integration Points
Depends on Linux types and ioctl. Integrates with old x86 BIOS APM firmware, power-management daemons, and legacy suspend/resume paths.

## Risks And Edge Cases
Modern systems generally use ACPI; APM firmware may be absent or buggy. Device id masks, OEM states, and resume event ordering are platform-specific.

## Test Signals
Legacy hardware/emulator standby/suspend tests, event delivery tests, absent-firmware error handling, and capability flag parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/apm_bios.h -->
