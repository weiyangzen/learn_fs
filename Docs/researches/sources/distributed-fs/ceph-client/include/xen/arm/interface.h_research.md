<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/interface.h -->
# sources/distributed-fs/ceph-client/include/xen/arm/interface.h

## Purpose
This header defines ARM Xen guest ABI helper types: aligned handles, pfn/long integer widths, primitive guest handles, maximum vCPU count, and pvclock structures.

## Important APIs, Types, And Functions
- `uint64_aligned_t` forces 8-byte alignment for ABI handle storage.
- `__DEFINE_GUEST_HANDLE`, `DEFINE_GUEST_HANDLE_STRUCT`, `DEFINE_GUEST_HANDLE`, `GUEST_HANDLE`, and `set_xen_guest_handle()` build Xen guest pointer handle types that work across 32/64-bit guests.
- `__HYPERVISOR_platform_op_raw` aliases the platform hypercall name.
- `xen_pfn_t`, `xen_ulong_t`, and `xen_long_t` are fixed 64-bit ABI types.
- Primitive guest handles are defined for char/int/void/uint64/uint32/pfn/ulong.
- `MAX_VIRT_CPUS` is one for this interface.
- `struct pvclock_vcpu_time_info` and `struct pvclock_wall_clock` provide packed time structures.

## Control Flow
There is no runtime control flow. Hypercall code populates guest handles with `set_xen_guest_handle()` before passing ABI structures to Xen.

## State And Persistence
No state is stored here. The structures define memory layout for shared ABI state exchanged with Xen.

## Dependencies And Integration Points
It depends on Linux integer types and is included by Xen public/arch interfaces and hypercall users. The guest-handle macros are central to grant, event, memory, and platform structures.

## Risks And Edge Cases
ABI packing/alignment must not change. `set_xen_guest_handle()` clears 64-bit storage before assigning the pointer, avoiding stale high bits on 32-bit guests; bypassing it risks invalid handles. `MAX_VIRT_CPUS` constrains this older ARM interface.

## Test Signals
Signals include compile-time ABI compatibility, correct handle layout on 32- and 64-bit ARM, hypercalls accepting handles, and pvclock readers handling packed structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/arm/interface.h -->
