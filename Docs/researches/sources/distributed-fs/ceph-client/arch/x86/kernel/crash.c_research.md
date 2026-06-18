# sources/distributed-fs/ceph-client/arch/x86/kernel/crash.c

## Purpose
Provides x86 crash-kexec shutdown, crash dump ELF header construction, crash-kernel memory map setup, segment loading, and crash hotplug ELF core header updates.

## Important APIs, Types, And Functions
`native_machine_crash_shutdown()` performs minimal machine shutdown for crash kexec. `crash_smp_send_stop()` and `kdump_nmi_shootdown_cpus()` stop other CPUs. `prepare_elf_headers()` builds RAM PT_LOAD headers excluding crash regions. `crash_setup_memmap_entries()` builds E820 entries for the dump kernel. `crash_load_segments()` loads ELF headers. `arch_crash_handle_hotplug_event()` updates elfcorehdr in place.

## Control Flow
Crash shutdown disables interrupts, stops other CPUs, disables virtualization and Intel PT, clears IO-APIC/LAPIC/HPET state, runs encrypted-guest kexec hooks, and saves CPU regs. File-based crash loading gathers RAM resources, excludes low 1M, crashkernel, low crashkernel, CMA, elf headers, and dm-crypt key ranges, then places ELF headers as a kexec segment. Hotplug rebuilds headers and copies them into the existing segment under temporary `kexec_crash_image` invalidation.

## State, Persistence, And Dependencies
State includes crash resources, kexec image fields, generated ELF headers, boot params E820 entries, and saved CPU notes. It depends on kexec, memblock/resource walking, APIC/IO-APIC/HPET, Intel PT, SEV/guest encryption hooks, and crash memory helpers.

## Integration Points
Hooks into panic/crash_kexec, kexec_file_load, crash hotplug, encrypted guest transitions, and dump-kernel boot parameter construction.

## Risks
Crash context is fragile: locks may be held, CPUs may be wedged, and only minimal operations are safe. Header sizing must account for maximum CPUs/memory ranges. Exclusion mistakes can cause dump kernel overwrite or missing memory.

## Test Signals
Crash dumps should boot reliably, include correct RAM ranges, exclude crashkernel/key/header regions, update elfcorehdr on CPU/memory hotplug, and avoid IO-APIC/APIC deadlocks during panic.
