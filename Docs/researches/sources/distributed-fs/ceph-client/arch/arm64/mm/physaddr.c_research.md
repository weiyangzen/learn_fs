# sources/distributed-fs/ceph-client/arch/arm64/mm/physaddr.c

## Purpose
This file provides debug-checked ARM64 virtual-to-physical conversion helpers. It warns when generic code uses `virt_to_phys()` on a non-linear-map address and validates that `__pa_symbol()` is used only for kernel image symbols.

## Important APIs, Types, and Functions
The exported functions are `__virt_to_phys()` and `__phys_addr_symbol()`. They wrap lower-level unchecked helpers `__virt_to_phys_nodebug()` and `__pa_symbol_nodebug()` with validation.

## Control Flow
`__virt_to_phys()` resets address tags with `__tag_reset()`, warns if the address is not in the linear map via `__is_lm_address()`, then returns the unchecked physical address. `__phys_addr_symbol()` uses `VIRTUAL_BUG_ON()` to assert the address falls between `KERNEL_START` and `KERNEL_END`, then returns the unchecked kernel-symbol physical address.

## State and Persistence
There is no persistent state. The functions provide runtime diagnostics and exported conversion behavior.

## Dependencies and Integration Points
The file integrates with generic callers of `virt_to_phys()` and `__pa_symbol()`, ARM64 memory-layout macros, MM debug infrastructure, and tag-reset helpers used on tagged architectures.

## Risks
The primary risk is caller misuse. `virt_to_phys()` on vmalloc/module/fixmap addresses is invalid and this wrapper warns to catch that. `__pa_symbol()` outside the kernel image is a bug and triggers a virtual-address bounds assertion.

## Test Signals
Debug builds should warn on intentional misuse tests. Normal boot and driver operation should not produce `virt_to_phys used for non-linear address` warnings. Symbol conversion users are indirectly tested by early page-table and memblock setup.
