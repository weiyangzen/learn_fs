# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/surestart-attributes.c

Purpose: adds the synthetic HP Sure Start sysfs object used to inspect firmware audit log availability and read audit log entries.

Important APIs/types/functions: `audit_log_entry_count_show()` returns count, entry size, and max entries. `audit_log_entries_show()` reads each log entry with `HPWMI_SURESTART_GET_LOG`. `hp_populate_sure_start_data()` creates the sysfs group; `hp_exit_sure_start_attributes()` removes it.

Control flow: the count file sends a Sure Start WMI query for log count. The entries file queries the count, rejects output larger than a page, then iterates 1-based log indices, requesting a 128-byte firmware buffer for each and copying the first 16 bytes into the sysfs output until failure or completion.

State and persistence: no persistent driver state except `bioscfg_drv.sure_start_attr_kobj`; logs live in firmware and are read-only through this driver.

Dependencies and integration: depends on `hp_wmi_perform_query()` and the synthetic object creation path in `bioscfg.c`.

Risks: sysfs binary-like output is constrained by `PAGE_SIZE`; future larger log formats would fail. `hp_exit_sure_start_attributes()` assumes the kobject exists. Test signals include zero logs, maximum logs, per-entry WMI failure returning partial data, page-size rejection, and removal during module exit.
