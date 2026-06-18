# sources/distributed-fs/ceph-client/drivers/rtc/rtc-efi.c

Purpose: exposes EFI firmware time services as a Linux RTC device on EFI-based systems. It supports read, set, and procfs capability reporting but no alarm.

Important APIs/types/functions: `convert_to_efi_time()` maps `struct rtc_time` to `efi_time_t`; `convert_from_efi_time()` validates and converts EFI fields back to RTC time. `compute_yday()` and `compute_wday()` fill derived fields. `efi_read_time()` calls `efi.get_time()`, while `efi_set_time()` calls `efi.set_time()`. `efi_procfs()` prints current EFI time and capability data.

Control flow: the platform probe first checks `efi.get_time()` works, allocates an RTC, clears `RTC_FEATURE_ALARM`, marks the device wake-capable, and registers it. Reads validate each EFI field range before returning to the RTC core. Writes always use unspecified timezone and map `tm_isdst` to EFI daylight flags.

State and persistence: persistent state lives entirely in EFI firmware/underlying platform RTC. The driver maintains no private state beyond the registered RTC.

Dependencies and integration: depends on global EFI runtime service pointers, platform driver probe, RTC core, and proc support through `rtc_class_ops.proc`.

Risks and test signals: firmware implementations vary; invalid EFI fields produce `-EIO`, and runtime-service failures map to `-EINVAL`. Timezone is not preserved on writes. Test usable/unusable EFI service paths, invalid firmware field rejection, DST flag mapping, proc capability output, and absence of alarm features.
