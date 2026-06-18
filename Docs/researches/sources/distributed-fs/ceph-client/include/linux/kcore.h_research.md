# sources/distributed-fs/ceph-client/include/linux/kcore.h

## Purpose
Declares the `/proc/kcore` memory range registration interface and range type identifiers.

## Important APIs, Types, And Functions
`enum kcore_type` classifies ranges as text, vmalloc, RAM, vmemmap, or user. `struct kcore_list` records a list node, address, size, and type. With `CONFIG_PROC_KCORE`, `kclist_add()` registers a range and `register_mem_pfn_is_ram()` installs a PFN classifier.

## Control Flow
Subsystems add memory ranges during initialization. `/proc/kcore` later walks the registered list to expose an ELF-core-like view of kernel memory. Disabled builds compile `kclist_add()` to a no-op.

## State And Persistence
Registered `kcore_list` entries are in-memory boot state. They are not persistent and represent current kernel virtual/physical layout.

## Dependencies And Integration Points
Depends on list infrastructure from including contexts and `CONFIG_PROC_KCORE`. Integrates with procfs, memory management, vmalloc, vmemmap, and debugging tools that inspect `/proc/kcore`.

## Risks
Incorrect ranges can expose invalid memory or omit useful debug areas. `/proc/kcore` has security implications because it describes kernel memory. Disabled builds silently ignore registrations.

## Test Signals
Signals include `/proc/kcore` ELF inspection, registered range presence, PFN classifier correctness, permission checks, and boot tests with and without `CONFIG_PROC_KCORE`.
