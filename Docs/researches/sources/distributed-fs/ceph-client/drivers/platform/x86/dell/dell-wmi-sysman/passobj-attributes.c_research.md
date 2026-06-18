## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/passobj-attributes.c

Purpose: implements password-object attributes under the sysman `authentication` kset. It exposes password status/limits and write-only files for current and new password handling.

Important APIs/functions: `alloc_po_data()` allocates password-object metadata. `populate_po_data()` caches attribute name and min/max password length, then creates sysfs files. `is_enabled_show()` re-queries firmware to report whether a password is set. `current_password_store()` copies user-provided current password into either `wmi_priv.current_admin_password` or `current_system_password` based on kobject name. `new_password_store()` strips a newline, bounds input, and calls `set_new_password()`. `role_show()` maps `Admin` to `bios-admin` and `System` to `power-on`.

Control flow: `sysman.c` enumerates password-object WMI instances into the `authentication` kset. Users first write the current password into a write-only buffer, then write the desired new password. Password interface code builds the WMI command and updates cached current password on success.

State and persistence: current passwords are stored in plaintext global buffers for the module lifetime. New passwords persist in firmware after a successful WMI call. The current-password sysfs file is write-only and does not validate against firmware at write time.

Dependencies and integration: sysfs kobject groups, shared sysman metadata, and `passwordattr-interface.c` for the actual WMI method.

Risks: plaintext password retention in kernel memory and lack of explicit clearing on module exit are security-sensitive. Length validation here only checks `MAX_BUFF`; firmware enforces min/max for actual password rules. Test signals include Admin/System role detection, unknown password-object names, current password newline trimming, maximum-length rejection, firmware unsupported/access-denied paths, and cleanup of authentication kobjects.
