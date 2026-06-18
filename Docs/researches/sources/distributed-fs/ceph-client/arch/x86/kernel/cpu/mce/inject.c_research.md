# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/inject.c

Purpose: implements the MCE injection test module, exposing debugfs controls for software decode-only records, hardware #MC injection, deferred-error interrupts, and threshold interrupts.

Important APIs and flow: debugfs files under `mce-inject` write fields in the global `i_mce` record (`status`, `misc`, `addr`, `synd`, `ipid`, `cpu`, `flags`, `bank`). Writing `bank` validates the target bank and triggers `do_inject()`. Software injection queues the record through `mce_log()`. Hardware and interrupt modes set MCA/SMCA MSRs on the target CPU with `prepare_msrs()`, temporarily enable HWCR injection, then trigger int18, deferred vector, or threshold vector. The module also registers a legacy mcelog injector notifier and an NMI handler for broadcast/random-context injection paths.

State and persistence: runtime state includes `i_mce`, injection type, hardware-injection availability, debugfs dentries, a cpumask for broadcast injection, and per-CPU `injectm` records used by MCE MSR wrappers. No persistence beyond module lifetime.

Dependencies and integration: depends on common MCE core, AMD SMCA/HWCR behavior, APIC/NMI/IPI delivery, debugfs, CPU hotplug read locks, legacy mcelog write notifier, and optional AMD northbridge PCI configuration.

Risks and test signals: hardware injection can panic the system by design, and platform firmware may block writes to status MSRs. Signals include debugfs mode parsing, software decode records, fake-panic-protected #MC injection, deferred/threshold vector delivery, invalid CPU/bank rejection, and cleanup on module unload.
