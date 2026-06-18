# sources/distributed-fs/ceph-client/arch/powerpc/boot/devtree.c

## Purpose
Boot-wrapper convenience layer for mutating and querying the flattened device tree before handing control to the kernel.

## Important APIs, Types, And Control Flow
Fixup APIs include `dt_fixup_memory()`, `dt_fixup_cpu_clocks()`, `dt_fixup_clock()`, `dt_fixup_mac_address_by_alias()`, `dt_fixup_mac_address()`, and `__dt_fixup_mac_addresses()`. Address helpers include `dt_get_reg_format()`, `dt_xlate_reg()`, `dt_xlate_addr()`, and `dt_get_virtual_reg()`. Compatibility matching is handled by `dt_is_compatible()`.

`dt_xlate()` is the core translation path: it reads a node's `reg`, walks parents, applies `ranges` translations using fixed-width address arrays up to four cells, checks address/size-cell limits, rejects unsupported PCI/special encodings, and returns a CPU physical/virtual address-sized result. `dt_get_virtual_reg()` prefers `virtual-reg` and falls back to translated `reg`.

## State, Dependencies, Risks, And Tests
State is the mutable FDT plus global `timebase_period_ns`; `prop_buf` is a shared scratch buffer. Dependencies include boot-wrapper DT ops (`finddevice`, `getprop`, `setprop`, aliases, parent traversal), endian helpers, and `MAX_PROP_LEN`. Risks include unsupported buses, static scratch buffer reuse, address truncation on 32-bit wrappers, `compare_reg()` boundary subtleties, division by zero if timebase is zero, and fatal exits on unsupported root cell counts. Test memory/clock/MAC fixups, `ranges` translation through nested buses, empty `ranges`, virtual-reg fallback, compatible lists with multiple strings, and 32-bit overflow rejection.
