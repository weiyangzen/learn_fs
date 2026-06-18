# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utlock.c

Purpose: `utlock.c` implements ACPICA's simple reader/writer lock abstraction using two OS mutexes and a reader count.

Important APIs/types/functions: `acpi_ut_create_rw_lock()` initializes `struct acpi_rw_lock` and creates reader and writer mutexes. `acpi_ut_delete_rw_lock()` deletes both mutexes and clears fields. `acpi_ut_acquire_read_lock()`/`acpi_ut_release_read_lock()` manage shared readers. `acpi_ut_acquire_write_lock()`/`acpi_ut_release_write_lock()` manage exclusive writers.

Control flow: The first reader acquires `writer_mutex`, blocking writers; subsequent readers only increment `num_readers` under `reader_mutex`. The last reader releases `writer_mutex`. Writers simply acquire and release `writer_mutex`. The comments acknowledge potential writer starvation but treat it as acceptable for ACPICA usage patterns.

State and persistence behavior: The persistent lock state is `num_readers`, `reader_mutex`, and `writer_mutex` in the caller-owned lock object. No global state is modified.

Dependencies and integration points: It depends on OSL mutex create/delete/acquire/release routines and ACPICA status codes. It is a utility for shared data structures that need many readers and infrequent writers.

Risks and test signals: Risks include writer starvation, failed creation of the second mutex leaking the first, reader count underflow on unmatched release, and deleting a lock with active readers/writers. Tests should cover multiple concurrent readers, writer exclusion, first-reader/last-reader transitions, second-mutex creation failure handling, and misuse assertions under debug/lock checking.
