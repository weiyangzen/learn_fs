## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/passwordattr-interface.c

Purpose: implements the Dell WMI password interface used by sysman password-object sysfs files to set Admin or System passwords.

Important APIs/functions: `call_password_interface()` evaluates WMI method 1 on `DELL_WMI_BIOS_PASSWORD_INTERFACE_GUID`, extracts integer status, sends a `KOBJ_CHANGE` uevent, and maps firmware status through `map_wmi_error()`. `set_new_password()` validates password type, selects the cached current password buffer, builds a command containing admin security area, password type, current password, and new password as UTF-16 length-prefixed strings, then calls the WMI method. Probe/remove callbacks update `wmi_priv.password_attr_wdev`.

Control flow: `new_password_store()` in `passobj-attributes.c` invokes `set_new_password()`. The function locks `wmi_priv.mutex`, builds all buffers, calls firmware, and on success copies the new value into the selected current password cache. On specific failures it logs missing admin password or invalid password hints.

State and persistence: password changes persist in firmware. Current Admin/System passwords are cached in plaintext global buffers, with the selected buffer updated after successful password change. The WMI device pointer is global and mutex-protected.

Dependencies and integration: WMI, sysman string/security buffer helpers, firmware-attributes class uevents, and password-object sysfs handlers.

Risks: the command uses the current admin password as the security area even when changing System password, which matches the intended firmware contract but must be documented. Plaintext buffers remain in memory. Output object type mismatches become generic `-EIO`. Test signals include Admin and System password changes, wrong-current-password failures, missing-admin-password firmware responses, uevent delivery for `is_enabled`, unknown password type, and concurrent password writes.
