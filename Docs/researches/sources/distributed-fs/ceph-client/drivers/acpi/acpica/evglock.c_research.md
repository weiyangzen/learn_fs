# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evglock.c

## Purpose
Implements ACPICA global lock support for non-reduced hardware. It installs the global-lock fixed event handler, maps absent hardware to mutex-only behavior, serializes host-side acquisition, performs the FACS global-lock hardware handshake, and releases the BIOS when pending.

## Important APIs, Types, And Functions
- `acpi_ev_init_global_lock_handler` installs the fixed event handler, creates the pending spin lock, and records whether global lock hardware is present.
- `acpi_ev_remove_global_lock_handler` removes the fixed event handler and deletes the pending lock.
- `acpi_ev_global_lock_handler` handles release interrupts and signals the global-lock semaphore when a request is pending.
- `acpi_ev_acquire_global_lock` acquires the OS mutex, updates the external handle, then loops on `ACPI_ACQUIRE_GLOBAL_LOCK` and waits for the semaphore if hardware ownership is not granted.
- `acpi_ev_release_global_lock` releases hardware ownership with `ACPI_RELEASE_GLOBAL_LOCK`, writes the global-lock release bit if BIOS is pending, clears acquired state, and releases the OS mutex.

## Control Flow
Initialization exits for reduced hardware or disabled global-lock use. Handler installation failure with `AE_NO_HARDWARE_RESPONSE` disables hardware global-lock use but is not fatal. Acquire first obtains a local mutex so only one ACPICA thread can contend for hardware, then either succeeds immediately in mutex-only mode or loops under the pending spin lock until FACS ownership is acquired. If the BIOS owns the lock, ACPICA marks `acpi_gbl_global_lock_pending`, releases the spin lock, waits on the semaphore signaled by the fixed event handler, and retries. Release writes the hardware release notification only when the pending bit is returned.

## State And Persistence
Global state includes `acpi_gbl_global_lock_present`, `acpi_gbl_global_lock_pending`, `acpi_gbl_global_lock_acquired`, `acpi_gbl_global_lock_handle`, global lock mutex/semaphore, pending spin lock, and FACS global-lock bits. The local OS mutex persists ownership across AML/external callers until release.

## Dependencies And Integration Points
Uses fixed event registration, ACPI bit-register writes, OS spin locks/mutexes/semaphores, interpreter wait helpers that can release the interpreter while blocking, and FACS global-lock macros.

## Risks And Edge Cases
Spurious release interrupts are ignored if no pending request exists. Absent hardware falls back to a standard mutex but later code can still identify that hardware is missing. Release without acquire returns `AE_NOT_ACQUIRED`. Timeout applies to local mutex acquisition, while hardware wait uses `ACPI_WAIT_FOREVER`, so firmware that never signals can hang the wait path.

## Test Signals
Validate no-op behavior in reduced/disabled modes, graceful handling of no hardware response, semaphore signaling only when pending, handle wraparound skipping zero, mutex-only acquire/release when hardware is absent, pending-bit release register writes, and warnings on unmatched release.
