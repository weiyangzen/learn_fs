# sources/distributed-fs/ceph-client/drivers/of/of_private.h

## Purpose
`of_private.h` is the internal contract for the OF core. It declares shared globals, conditional stubs, internal helpers, FDT constants, reserved-memory entry points, DMA hooks, address bounds, and transaction iteration macros not intended as public OF API.

## Important APIs, types, and functions
The key type is `struct alias_prop`, shared by alias scanning and uevent code. Important declarations include `of_mutex`, `devtree_lock`, `aliases_lookup`, `of_kset`, dynamic change helpers, sysfs attach/update helpers, overlay locks, `__unflatten_device_tree()`, `of_alias_scan()`, `__of_prop_dup()`, `__of_node_dup()`, internal path/property mutation helpers, `__of_detach_node()`, `of_dma_get_range()`, `__of_get_dma_parent()`, `fdt_scan_reserved_mem()`, `fdt_scan_reserved_mem_late()`, and `of_fdt_device_is_available()`.

## Control flow and state
The header selects real implementations or no-op stubs based on config symbols such as `CONFIG_OF_DYNAMIC`, `CONFIG_OF_KOBJ`, `CONFIG_OF_ADDRESS`, `CONFIG_HAS_DMA`, `CONFIG_OF_OVERLAY`, and KUnit/unit-test settings. It also defines default root cell counts, reserved-memory limits, illegal phandle marker, maximum address cells, and validation macros used by early FDT address translation.

## Dependencies and integration
This header is included by the OF core C files in this subset and coordinates boundaries between base traversal, dynamic mutation, sysfs mirroring, FDT boot code, reserved memory, DMA address parsing, IRQ parsing, overlays, and tests.

## Risks and test signals
The main risk is contract drift: changing a stub or declaration can silently alter behavior for many config combinations. Locking declarations and underscored helper comments are especially important because callers may bypass normal references and locking only on detached trees or under locks. Build coverage across config matrices is the primary test signal.
