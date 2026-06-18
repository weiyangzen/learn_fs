
# sources/distributed-fs/ceph-client/arch/x86/include/asm/crash.h

Purpose: x86 crash-kernel and kexec crash support declarations.

Important APIs and control flow: declares `crash_load_segments()`, `crash_setup_memmap_entries()`, and `crash_smp_send_stop()`. Implementations prepare crash image segments, populate boot-parameter memory maps, and stop secondary CPUs during crash transitions.

State, dependencies, and risks: state includes `struct kimage`, boot params, memory maps, and CPU stop state. Dependencies include kexec, e820/bootparam code, and SMP IPI/stop machinery. Risks include bad crash memory maps, failure to quiesce CPUs, and differences between normal and panic contexts. Test signals are kdump boot tests, crashkernel reservation tests, and panic/kexec integration.
