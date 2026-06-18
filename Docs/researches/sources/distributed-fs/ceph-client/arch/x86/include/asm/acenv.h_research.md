## `sources/distributed-fs/ceph-client/arch/x86/include/asm/acenv.h`

Purpose: x86 ACPICA environment hooks for cache flush, global lock operations, and integer math helpers.

Important APIs and macros: `ACPI_FLUSH_CPU_CACHE()` flushes CPU caches with `wbinvd()` except under a hypervisor. `__acpi_acquire_global_lock()` and `__acpi_release_global_lock()` back ACPICA global lock macros. `ACPI_DIV_64_BY_32()` and `ACPI_SHIFT_RIGHT_64()` provide inline x86 assembly arithmetic helpers for ACPICA.

Control flow: sleep-state cache flushing checks `X86_FEATURE_HYPERVISOR` to avoid unnecessary host-impacting flushes in VMs. Global lock macros pass the FACS global lock field address to arch functions.

State and persistence: global lock state lives in ACPI FACS memory; this header does not store state.

Dependencies and integration points: ACPICA core, x86 special instructions, CPU feature detection, and ACPI sleep/global-lock code.

Risks: cache flush bypass in guests assumes VM sleep state cannot cause host data loss. Inline asm constraints must be correct for ACPICA arithmetic users. Global lock functions must implement ACPI locking semantics.

Test signals: ACPI suspend/resume on bare metal and VMs, ACPICA build, and global-lock firmware interactions.
