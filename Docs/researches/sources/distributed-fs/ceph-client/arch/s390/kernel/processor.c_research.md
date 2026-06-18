# sources/distributed-fs/ceph-client/arch/s390/kernel/processor.c

Purpose: provides s390 CPU identity, HWCAP/platform setup, CPU frequency reporting, CPU relax/yield behavior, text-patching synchronization, per-CPU initialization, and `/proc/cpuinfo` rendering.

Important APIs/functions: exported or architecture-visible functions include `cpu_detect_mhz_feature()`, `s390_update_cpu_mhz()`, `stop_machine_yield()`, `text_poke_sync()`, `text_poke_sync_lock()`, `cpu_init()`, and `cpuinfo_op`. Initcalls `setup_hwcaps()` and `setup_elf_platform()` populate ELF auxiliary-vector capability state. Helpers render facilities, cache info, topology, IDs, and MHz data.

Control flow: early boot detects whether ECAG CPU MHz attributes are available. MHz updates adjust jiffies and run an on-each-CPU ECAG query. Stop-machine spin loops periodically yield to preempted target virtual CPUs. Text patching broadcasts `sync_core()` to all CPUs, optionally under the CPU read lock. `cpu_init()` captures the CPU ID, initializes dynamic/static MHz, attaches `init_mm` as `active_mm`, and enters lazy TLB mode. HWCAP setup checks facility bits and machine features, then sets ELF flags for vector, guarded storage, NNPA, DFLT, SORT, SIE, and other capabilities. Platform setup maps machine IDs to strings such as `z13`, `z16`, or `z17`.

State and persistence: global `elf_hwcap` and `elf_platform` become user ABI through ELF aux vectors. Per-CPU `cpu_info` stores dynamic/static MHz and CPUID. Per-CPU `cpu_relax_retry` throttles yield attempts. State is runtime-only but visible through `/proc/cpuinfo`.

Dependencies and integration points: depends on ECAG, STFL facility lists, CPU feature helpers, SCLP virtualization flags, scheduler topology, cacheinfo, SMP CPU masks, text patching, stop_machine, `init_mm`, and ELF core/loader interfaces.

Risks: HWCAP bits are userspace ABI and must only be set when instructions are truly available. Platform strings guide optimized libraries. Text-patching synchronization must reach all online CPUs. CPU MHz reporting is optional and must tolerate machines without the ECAG attribute. Virtual CPU yielding must avoid excessive hypervisor calls.

Test signals: `/proc/cpuinfo` should show correct feature strings, facilities, topology, machine IDs, and MHz fields; auxv should expose expected HWCAP bits; text patching and alternatives should synchronize under SMP; stop_machine loops under virtualization should make forward progress; boot on new machine IDs should choose a sensible platform string.
