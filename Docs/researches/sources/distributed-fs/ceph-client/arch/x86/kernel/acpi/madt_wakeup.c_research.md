# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/madt_wakeup.c

## Purpose
`madt_wakeup.c` implements x86 support for the ACPI MADT Multiprocessor Wakeup structure. It allows secondary CPU startup through a firmware mailbox instead of legacy INIT/SIPI, and, for version 1 wakeup structures, configures CPU offlining handoff through an ACPI reset vector.

## Important APIs, Types, and Functions
- Persistent addresses: `acpi_mp_wake_mailbox_paddr`, `acpi_mp_wake_mailbox`, `acpi_mp_pgd`, and `acpi_mp_reset_vector_paddr`.
- CPU teardown callbacks: `acpi_mp_stop_this_cpu()`, `acpi_mp_play_dead()`, and `acpi_mp_cpu_die()`.
- Mapping setup: `alloc_pgt_page()`, `free_pgt_page()`, and `acpi_mp_setup_reset()`.
- Startup callback: `acpi_wakeup_cpu()` writes APIC ID, wakeup vector, and command into the ACPI mailbox.
- Policy fallback: `acpi_mp_disable_offlining()` disables CPU offlining and clears the MADT mailbox address for kexec convention.
- Entry point: `acpi_parse_mp_wake()` validates and parses the MADT subtable and updates APIC startup callbacks.

## Control Flow
`boot.c` parses the MADT MP Wake subtable and calls `acpi_parse_mp_wake()`. The parser validates the minimum v0 structure, records the mailbox physical address, and, when v1 reset-vector data is present, calls `acpi_mp_setup_reset()`. Reset setup builds a new identity page table over all `pfn_mapped[]` ranges, maps the reset-vector page, maps the `asm_acpi_mp_play_dead()` page at its kernel virtual offset, and then installs SMP callbacks for play-dead, stop-this-CPU, and CPU-die. If reset setup fails or the structure is only v0, CPU offlining is disabled.

Secondary CPU wakeup is serialized by the CPU bringup core. On first use, `acpi_wakeup_cpu()` `memremap()`s the mailbox, writes APIC ID and wake vector, publishes the wake command with `smp_store_release()`, and spins until firmware clears the command. CPU die confirmation uses a test command and a one-second timeout to verify firmware has taken control.

## State and Persistence Behavior
Mailbox physical address and reset-vector identity mapping state are initialized once and marked read-mostly/after-init where applicable. The mailbox remains mapped after first use. `acpi_mp_disable_offlining()` mutates the in-memory MADT wakeup structure by zeroing `mailbox_address` to prevent a kexec kernel from using an invalid inherited mailbox; this is a Linux convention rather than ACPI-defined persistence.

## Dependencies and Integration Points
This file integrates ACPI MADT parsing, x86 APIC secondary wakeup callbacks, SMP hotplug callbacks, memblock page-table allocation, kernel identity mappings, CPU hotplug policy, kexec safety, NMI/APIC/processor headers, and the assembly routine in `madt_playdead.S`.

## Risks
- Firmware mailbox command ordering is critical; APIC ID and wake vector must be visible before the command.
- The wake loop intentionally waits indefinitely to avoid TDX/VMM delayed-wakeup attacks; a broken firmware path can hang bringup.
- Identity-map construction failures disable offlining and can limit kexec secondary CPU use.
- Clearing the MADT mailbox for kexec is Linux-specific and assumes the running kernel has already cached the mailbox address.

## Test Signals
- Boot on systems advertising `ACPI_MADT_TYPE_MULTIPROC_WAKEUP`; verify secondary CPU startup uses `acpi_wakeup_cpu`.
- Test CPU hotplug/offline on v1 structures and verify offlining is disabled on v0 or failed reset setup.
- Test kexec after MP wakeup parsing to ensure the second kernel does not misuse an invalid mailbox.
- Validate TDX or delayed-vCPU environments do not prematurely abort wakeup.
