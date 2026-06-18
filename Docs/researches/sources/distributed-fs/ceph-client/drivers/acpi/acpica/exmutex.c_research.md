# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exmutex.c

## Purpose
`exmutex.c` implements AML mutex acquire/release behavior, including SyncLevel ordering, recursive acquisition by the same thread, global lock special handling, and forced release at interpreter thread exit.

## Important APIs, Types, And Functions
Public/internal functions are `acpi_ex_acquire_mutex_object`, `acpi_ex_acquire_mutex`, `acpi_ex_release_mutex_object`, `acpi_ex_release_mutex`, `acpi_ex_unlink_mutex`, and `acpi_ex_release_all_mutexes`; `acpi_ex_link_mutex` is private. Important state lives in `union acpi_operand_object` mutex fields and `struct acpi_thread_state` acquired-mutex list/current sync level.

## Control Flow
Low-level acquire supports recursive acquisition by the owning thread by incrementing acquisition depth. Otherwise it waits on either the ACPI global lock or OS mutex, then records thread ID and depth. AML acquire first validates thread state and SyncLevel ordering, delegates to low-level acquire, then on first acquisition stores owner thread, original sync level, updates current sync level, and links the mutex into the thread's acquired list. Low-level release decrements depth, unlinks when depth reaches zero, releases global lock or OS mutex, and clears thread ID. AML release validates ownership, thread ID, and SyncLevel equality, restores the prior sync level from the list head's saved value after final release, and handles same-level non-LIFO releases. Forced release walks the acquired list at thread exit and releases every held mutex while clearing ownership fields.

## State And Persistence
Mutex ownership, acquisition depth, owner thread, current/original SyncLevel, and acquired-list links are mutable runtime state. Global lock acquire/release also affects firmware global lock state through event helpers.

## Dependencies And Integration Points
The file integrates OS mutex waits/releases, ACPI global lock event helpers, interpreter lock expectations, and external global lock APIs in `evxface.c`.

## Risks
SyncLevel rules are the main deadlock prevention mechanism; bypassing them or corrupting list links can leave methods deadlocked. Forced release intentionally releases all held mutexes at thread exit, which may mask method bugs but prevents permanent lock leaks. Global lock has special ownership semantics allowing release by other threads in one path.

## Test Signals
Tests should cover recursive acquire/release depth, timeout failures, SyncLevel ordering rejection, non-owner release rejection, same-level non-LIFO release restoration, forced release cleanup, global lock special case, and acquired-list link/unlink integrity.
