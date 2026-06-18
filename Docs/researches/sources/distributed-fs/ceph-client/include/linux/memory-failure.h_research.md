<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory-failure.h -->
# sources/distributed-fs/ceph-client/include/linux/memory-failure.h

## Purpose
This header defines a registration interface for mapping poisoned PFNs back to address spaces and VM offsets during memory-failure handling.

## Important APIs, types, and functions
`struct pfn_address_space` embeds an interval tree node, an `address_space *mapping`, and a `pfn_to_vma_pgoff` callback. `register_pfn_address_space()` and `unregister_pfn_address_space()` are available with `CONFIG_MEMORY_FAILURE`; disabled builds return `-EOPNOTSUPP` or no-op.

## Control flow
Subsystems that manage PFN-backed mappings register an interval with a callback so memory-failure code can translate a poisoned PFN into the affected VMA page offset and notify or kill users appropriately.

## State and persistence
Registered intervals are runtime memory-failure lookup state. No persistent data is stored by the header.

## Dependencies and integration points
It depends on interval trees, address spaces, VMAs, PFNs, and memory-failure configuration. It integrates DAX/device memory style mappings with hwpoison handling.

## Risks and test signals
Risks include stale interval registrations, wrong PFN-to-offset translation, disabled-config callers ignoring `-EOPNOTSUPP`, and races with unmap/remove. Test register/unregister, poisoned PFNs inside and outside intervals, VMA offset conversion, and module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memory-failure.h -->
