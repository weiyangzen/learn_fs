# sources/distributed-fs/ceph-client/samples/bpf/cpustat_user.c

Purpose: userspace loader and terminal display for the CPU state BPF sample.

Important APIs/types/functions: uses libbpf object/program APIs, map FDs `cstate_map_fd` and `pstate_map_fd`, `cpu_stat_update`, `cpu_stat_print`, `cpu_stat_inject_cpu_idle_event`, `cpu_stat_inject_cpu_frequency_event`, signal handler `int_exit`, and sysfs path `/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq`.

Control flow: opens `<argv[0]>_kern.o`, finds `bpf_prog1`, loads the object, finds duration maps, attaches one program, injects idle/frequency events, then loops every five seconds reading maps and printing a screen-cleared table. Signal exit injects final events, updates/prints stats, and exits.

State and persistence: keeps latest map values in `stat_data`. BPF links and object persist until process exit or cleanup. It writes CPU frequency sysfs values as an event trigger.

Dependencies and integration: pairs with `cpustat_kern.c`, requires libbpf, power tracepoints, CPUFreq sysfs, scheduling affinity APIs, and sufficient privilege for BPF and sysfs writes.

Risks: only attaches `bpf_prog1` explicitly despite the object also containing `bpf_prog2`, depending on libbpf auto-attach behavior is not obvious. Frequency constants are platform-specific and `CPUFREQ_HIGHEST_FREQ` appears one zero larger than the documented 1.2 GHz value. Signal handler does non-async-safe work.

Test signals: run on a compatible platform, observe table updates, verify both cstate and pstate maps receive values, and test SIGINT final print behavior.
