## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cputime.h

Purpose: implements PowerPC virtual CPU accounting hooks when native timebase accounting is enabled.

Important APIs/types/functions: `cputime_to_nsecs()`, `get_accounting()`, `raw_get_accounting()`, `account_cpu_user_entry()`, `account_cpu_user_exit()`, and `account_stolen_time()`.

Control flow: user entry/exit helpers read the timebase with `mftb()`, update unreconciled user/system start times, and avoid tracing. On SPLPAR, stolen-time accounting checks the lppaca dispatch trace index and calls `pseries_accumulate_stolen_time()` when it changed.

State and persistence: updates per-CPU/per-task `cpu_accounting_data`, stored in PACA on PPC64 and `thread_info` on PPC32. It reads lppaca DTL state for hypervisor stolen time.

Dependencies and integration: depends on `asm/time.h`, `asm/firmware.h`, `PACA`, SPLPAR firmware feature detection, and scheduler/accounting paths. Generic no-op stubs are emitted without native accounting.

Risks and test signals: these helpers run in sensitive entry/exit paths and cannot trace. Wrong start-time updates skew user/system/stolen accounting. Test signals include `CONFIG_VIRT_CPU_ACCOUNTING_NATIVE` builds, pseries SPLPAR workloads, `/proc/stat` accounting checks, context-switch stress, and tracing recursion checks.
