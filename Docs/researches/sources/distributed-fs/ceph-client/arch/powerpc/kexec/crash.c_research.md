# sources/distributed-fs/ceph-client/arch/powerpc/kexec/crash.c

## Purpose
Implements PowerPC crash-kexec CPU stopping, crash shutdown handler registration, crash CPU state saving, backup-region ELF synchronization, and crash hotplug updates.

## Important APIs, Types, And Functions
Defines `crash_ipi_callback`, `crash_kexec_secondary`, `crash_kexec_prepare`, `crash_shutdown_register`, `crash_shutdown_unregister`, `default_machine_crash_shutdown`, `sync_backup_region_phdr`, `machine_kexec_post_load`, `arch_crash_get_elfcorehdr_size`, `arch_crash_hotplug_support`, and `arch_crash_handle_hotplug_event`. Internal helpers include `handle_fault`, `crash_kexec_prepare_cpus`, `crash_kexec_wait_realmode`, `update_crash_elfcorehdr`, `get_fdt_index`, and `update_crash_fdt`.

## Control Flow
On crash, the crashing CPU disables hard IRQs, records `crashing_cpu`, and tries to stop other CPUs through IPIs or system-reset rendezvous. Secondaries save their registers once, increment `cpus_in_crash`, wait for `time_to_dump`, call platform CPU-down hooks, and park. The primary saves CPU state, marks dumping ready, waits for real mode, masks interrupts, runs registered crash shutdown handlers under a setjmp/longjmp fault guard, and calls platform CPU-down hooks. Hotplug support can rebuild the crash ELF core header or refresh CPU nodes in the crash FDT while temporarily invalidating `kexec_crash_image`.

## State And Persistence
State includes `time_to_dump`, `is_via_system_reset`, `crash_wake_offline`, crash shutdown handler slots, fault-recovery jump buffer, `crash_shutdown_cpu`, `cpus_in_crash`, saved per-CPU crash notes, backup region offsets, and live crash image segment contents.

## Dependencies And Integration Points
Integrates with generic crash kexec, PowerPC debugger fault hooks, SMP IPIs, platform `kexec_cpu_down`, ELF core header generation, memory/CPU hotplug, libfdt, and `update_cpus_node` from `core_64.c`.

## Risks And Edge Cases
Crash code runs after the kernel may be corrupt. CPUs may not respond to IPIs, so system reset fallback and timeouts matter. Shutdown handlers can fault and are bounded to three entries. Hotplug rewriting of live crash segments must avoid exposing a partially updated image.

## Test Signals
Crash dump end-to-end tests, nonresponsive CPU scenarios, system-reset crash entry, registered shutdown handler fault injection, backup-region offset checks, CPU add/remove crash hotplug, memory add/remove crash hotplug, and vmcore readability are important.
