# sources/distributed-fs/ceph-client/include/linux/types.h

## Purpose
Defines common in-kernel type aliases, scalar typedefs, list/RCU callback structures, atomic placeholders, address-size types, and utility function pointer types.

## Important APIs, Types, And Functions
Key exports include bitmap declaration macro, 128-bit aliases when supported, device/inode/mode/pid/time typedefs, `bool`, uid/gid types, `size_t`, `ssize_t`, BSD/SysV aliases, fixed-width integer aliases, aligned 64-bit aliases, `ktime_t`, `sector_t`, `blkcnt_t`, `dma_addr_t`, `gfp_t`, `phys_addr_t`, `resource_size_t`, `irq_hw_number_t`, `atomic_t`, `atomic64_t`, `rcuref_t`, `list_head`, `hlist_head`, `hlist_node`, `ustat`, `callback_head`/`rcu_head`, callback typedefs, swap/cmp function typedefs, and `struct rcuwait`.

## Control Flow
No runtime control flow is implemented. The header conditions type widths on architecture/config symbols such as DMA and physical address width.

## State, Persistence, And Dependencies
This is foundational compile-time type state. It includes UAPI Linux types and excludes most definitions under assembly. Alignment of `callback_head` is a correctness requirement for RCU/page tail bit encoding.

## Integration Points
Included throughout the kernel; every subsystem depends on its aliases and list/RCU base structures. It bridges UAPI type definitions to internal kernel names.

## Risks And Test Signals
Risks include ABI/type-width mismatches across architectures, redefinition conflicts with compiler/libc names, and alignment regressions in RCU callback structures. Test signals are allmodconfig builds, sparse bitwise type checks, 32/64-bit architecture builds, and compile checks for DMA/phys address width configs.
