## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utmutex.c

Purpose: `utmutex.c` owns ACPICA internal synchronization object lifecycle and acquire/release wrappers for the predefined global mutex set, spinlocks, raw locks, the `_OSI` mutex, and the namespace reader/writer lock.

Important APIs and functions: `acpi_ut_mutex_initialize` creates every `acpi_gbl_mutex_info[]` mutex, `acpi_gbl_gpe_lock`, `acpi_gbl_hardware_lock`, `acpi_gbl_reference_count_lock`, `acpi_gbl_osi_mutex`, and `acpi_gbl_namespace_rw_lock`. `acpi_ut_mutex_terminate` deletes them. `acpi_ut_acquire_mutex` and `acpi_ut_release_mutex` validate mutex IDs, delegate to the OS mutex layer, and update owner thread/use-count bookkeeping. Static helpers `acpi_ut_create_mutex` and `acpi_ut_delete_mutex` perform per-entry lifecycle work.

Control flow: initialization loops through the fixed mutex IDs, then creates lock classes in dependency order. Acquire obtains the current thread ID, optionally checks strict mutex ordering under `ACPI_MUTEX_DEBUG`, waits forever on the OS mutex, and records ownership. Release checks validity and acquired state, optionally validates release order, clears owner state first, then releases the OS mutex.

State and dependencies: persistent global state includes OS mutex pointers, owning thread IDs, use counts, spinlock handles, and the namespace rwlock. The file depends on ACPICA OS services for mutex/lock creation and thread IDs.

Integration points: owner ID allocation, memory tracking, namespace access, event/GPE paths, `_OSI`, and subsystem initialization all depend on these locks being initialized first and terminated after subsystem shutdown.

Risks: partial initialization failure does not unwind previously created locks in this file, so callers must handle failed subsystem initialization carefully. Deadlock prevention is debug-only; production relies on correct lock ordering.

Test signals: init/terminate cycles, invalid mutex IDs, double release, same-thread reacquire under debug, and ordered nested acquire/release sequences are the main behavioral checks.
