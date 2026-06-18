# sources/distributed-fs/ceph-client/arch/sh/kernel/nmi_debug.c

Purpose: provides boot-time configurable NMI diagnostics through the die notifier chain.

Important APIs and control flow: `nmi_debug_setup()` registers a notifier and parses `nmi_debug=` comma options: `state`, `regs`, `debounce`, and `die`. `nmi_debug_notify()` handles `DIE_NMI` by optionally calling `show_state()`, `show_regs()`, delaying 10 ms, and returning `NOTIFY_BAD` to force fatal behavior when requested.

State, dependencies, and risks: state is the `nmi_actions` bitmask and registered notifier. Dependencies include die notifier ordering, NMI trap handling, scheduler state dump, and `show_regs()`. Risks include unsafe work in NMI context, debounce delays during critical faults, and notifier side effects when enabled without actions. Test signals are boot-parameter parsing, synthetic/platform NMI, and verifying requested state/regs/die behavior.
