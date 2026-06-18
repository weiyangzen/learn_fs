<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsinit.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsinit.c

## Purpose
Completes ACPICA namespace initialization after table load. It initializes deferred objects, runs device initialization methods, initializes address-space regions, and invokes global initialization handlers.

## Important APIs, Types, And Functions
Key routines are `acpi_ns_initialize_objects`, `acpi_ns_initialize_devices`, `acpi_ns_init_one_package`, and callbacks `acpi_ns_init_one_object`, `acpi_ns_find_ini_methods`, and `acpi_ns_init_one_device`. It uses `struct acpi_init_walk_info`, `struct acpi_device_walk_info`, `_STA`, `_INI`, `_REG`, and flags such as `ANOBJ_SUBTREE_HAS_INI`.

## Control Flow
Object initialization walks the namespace, counts objects, and initializes deferred package/bank-field data under the interpreter lock. Device initialization optionally scans for `_INI` methods and bubbles `ANOBJ_SUBTREE_HAS_INI` up ancestors, allocates shared evaluation info, runs root `_INI` and `\_SB._INI`, initializes operation regions unless disabled, then walks present device/processor/thermal objects. Each device checks subtree tagging, evaluates `_STA`, prunes absent nonfunctional subtrees, skips `_INI` for absent-but-functional bridge-like nodes, evaluates `_INI` when present, and calls the global init handler.

## State And Persistence
Sets package data-valid flags, subtree-has-INI flags, global truncate-I/O-address compatibility after `_OSI` use, operation-region handler state through event code, and counters used for diagnostics.

## Dependencies And Integration Points
Depends on namespace walking, dispatcher deferred-argument initialization, interpreter locking, event/op-region initialization, `_STA` execution helpers, `acpi_ns_evaluate`, and global init callbacks.

## Risks And Edge Cases
Initialization intentionally ignores many per-object errors to continue booting. `_STA` semantics control subtree pruning and can hide children if firmware reports absent/nonfunctional. `\_SB._INI` ordering before `_REG` is compatibility-sensitive. Shared evaluation info must be cleared between method calls.

## Test Signals
Boot tests with devices containing `_INI`, absent `_STA`, absent/functioning bridge states, failing `_INI`, operation regions requiring `_REG`, deferred packages with forward references, and `_OSI` calls that should enable I/O truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsinit.c -->
