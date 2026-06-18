# sources/distributed-fs/ceph-client/include/acpi/platform/aclinuxex.h

Purpose: Supplies Linux-kernel late ACPICA OSL declarations and inline/macro implementations for allocation, object-cache allocation, thread-id retrieval, raw lock operations, debugger setup, and optional 64-bit math fallbacks.

Important APIs, types, and functions: Declares `acpi_os_initialize()` and `acpi_os_terminate()`, defines `acpi_os_allocate()`, `acpi_os_allocate_zeroed()`, `acpi_os_acquire_object()`, `acpi_os_free()`, `acpi_os_get_thread_id()`, `acpi_os_create_lock()`, `acpi_os_create_raw_lock()`, raw acquire/release/delete helpers, `acpi_os_readable()`, debugger init/terminate stubs, and math macros `ACPI_DIV_64_BY_32` and `ACPI_SHIFT_RIGHT_64` if native divide is unavailable.

Control flow: Allocators choose `GFP_ATOMIC` when interrupts are disabled and `GFP_KERNEL` otherwise. Lock creation allocates Linux spinlock/raw-spinlock objects and initializes them. Raw acquire/release save and restore interrupt flags.

State and persistence: Allocated locks and cache objects are runtime kernel memory. There is no persistent state.

Dependencies and integration points: Depends on Linux `kmalloc`, `kzalloc`, `kmem_cache_zalloc`, `kfree`, `current`, spinlocks, raw spinlocks, `do_div`, and interrupt-state helpers. Used by ACPICA OSL internals.

Risks and test signals: Risks are sleeping allocations during resume/IRQ-off paths, lockdep false positives, raw lock lifetime leaks, and math fallback errors on 32-bit systems. Test boot/resume allocation paths, ACPI table parsing under IRQ-off resume, lockdep, 32-bit non-native divide builds, and ACPI debugger stubs.
