# sources/distributed-fs/ceph-client/include/linux/sched/nohz.h

Purpose: declares the scheduler interface to NOHZ/dynticks balancing, load accounting, and remote CPU wakeups.

Important APIs and types: `nohz_balance_enter_idle()`, `get_nohz_timer_target()`, `calc_load_nohz_start()`, `calc_load_nohz_remote()`, `calc_load_nohz_stop()`, and `wake_up_nohz_cpu()` are exported under `CONFIG_NO_HZ_COMMON`, with no-op fallbacks otherwise.

Control flow: idle CPUs enter NOHZ balance state, load accounting starts/stops tickless adjustments, remote load updates may be performed for idle runqueues, and wakeups kick tickless CPUs when scheduler work is needed.

State and persistence: state is runtime NOHZ scheduler/load metadata maintained in scheduler core and runqueues.

Dependencies and integration points: integrates scheduler balancing and loadavg with tickless idle/full-nohz infrastructure.

Risks and test signals: risks include stale load averages from idle CPUs, missed remote wakeups, and no-op fallback drift. Test NOHZ idle, nohz_full, loadavg under idle transitions, remote wakeups to tickless CPUs, and non-NOHZ builds.
