# sources/distributed-fs/ceph-client/fs/resctrl/Makefile

Purpose: Builds the resctrl filesystem objects according to Kconfig selections and sets a local include path for trace header generation.

Important APIs, types, and functions: Uses `obj-$(CONFIG_RESCTRL_FS)` for `rdtgroup.o`, `ctrlmondata.o`, and `monitor.o`; uses `obj-$(CONFIG_RESCTRL_FS_PSEUDO_LOCK)` for `pseudo_lock.o`; sets `CFLAGS_monitor.o = -I$(src)`.

Control flow: If `RESCTRL_FS` is enabled, the core group, control/monitor data, and monitor implementation objects are linked. If pseudo-locking is enabled, the pseudo-lock object is added. `monitor.o` receives the source directory include path so `define_trace.h` recursive include expectations are satisfied.

State and persistence: No runtime state is defined here. Build selections determine which resctrl runtime features exist.

Dependencies and integration points: Integrates Kbuild with Kconfig symbols from `fs/resctrl/Kconfig` and with tracepoint header include mechanics.

Risks and test signals: Risks are missing objects under a config, trace include failures, or pseudo-lock object linkage without its dependencies. Test all relevant resctrl config combinations and confirm `monitor.o` trace compilation succeeds.
