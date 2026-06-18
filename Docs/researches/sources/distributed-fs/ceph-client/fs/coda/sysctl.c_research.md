# sources/distributed-fs/ceph-client/fs/coda/sysctl.c

Purpose: registers Coda runtime tunables under the `coda` sysctl table when `CONFIG_SYSCTL` is enabled.

Important APIs/functions: `coda_table` exposes `timeout`, `hard`, and `fake_statfs` using `proc_dointvec`. `coda_sysctl_init()` registers the table once through `register_sysctl("coda", coda_table)`. `coda_sysctl_clean()` unregisters and clears the saved table header.

Control flow: `psdev.c` calls init during Coda module/device setup and clean during failure or module exit. Runtime reads/writes update the global variables consumed by upcall waiting and statfs behavior.

State and persistence: persistent kernel state is the sysctl table header plus globals `coda_timeout`, `coda_hard`, and `coda_fake_statfs`; values do not persist across reboot/module reload.

Dependencies/integration: depends on `linux/sysctl.h` and declarations in `coda_int.h`. `coda_timeout` and `coda_hard` control signal/timeout behavior in `upcall.c`; `coda_fake_statfs` is declared by Coda Linux support and influences statfs policy outside this file.

Risks: no min/max handlers are applied, so invalid values can be written by privileged users and later code must tolerate them. Registration is guarded only by `fs_table_header`, so init/cleanup pairing matters.

Test signals: sysctl registration/unregistration on module load/unload, reads and writes for all three knobs, negative/large timeout behavior in upcall waits, and absence of sysctl calls when built without `CONFIG_SYSCTL`.
