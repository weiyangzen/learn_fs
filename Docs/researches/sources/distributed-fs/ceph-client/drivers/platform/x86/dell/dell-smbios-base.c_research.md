# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smbios-base.c

Purpose: Common Dell SMBIOS calling-interface core. It discovers DMI tokens, registers WMI/SMM backends, arbitrates calls by priority, filters unsafe userspace requests, exposes token sysfs data, and provides helper APIs.

Important APIs/types/functions: Exports backend registration, `dell_smbios_call_filter()`, `dell_smbios_call()`, `dell_fill_request()`, `dell_send_request()`, token lookup, laptop notifier helpers, and class support. Internal state includes supported command bitmap, token array, backend list, sysfs token data, and mutex.

Control flow/state/persistence: Init rejects non-Dell/Alienware systems, walks DMI type `0xda`, registers a platform device, initializes WMI and SMM backends, and builds `tokens/` sysfs. Calls choose the highest-priority backend. Filters blacklist dangerous classes/tokens and require capabilities for privileged calls. State is memory-only from DMI.

Dependencies/integration: DMI, platform devices, capabilities, sysfs, WMI/SMM backend init, and all Dell SMBIOS clients such as `dell-laptop` and `dell-pc`.

Risks/test signals: Security filtering is critical. Test blacklist/whitelist behavior, capability checks, duplicate token zeroing, backend priority/failure, token sysfs permissions, and notifier delivery.
