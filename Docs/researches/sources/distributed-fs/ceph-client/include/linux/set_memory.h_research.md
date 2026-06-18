# sources/distributed-fs/ceph-client/include/linux/set_memory.h

## Purpose

`set_memory.h` provides a cross-architecture API for changing kernel page attributes, direct-map validity, machine-check mitigation attributes, and memory encryption state. It supplies real architecture implementations when configured and no-op fallbacks when not supported.

## Important APIs, Types, And Functions

Primary APIs are `set_memory_ro()`, `set_memory_rw()`, `set_memory_x()`, `set_memory_nx()`, `set_memory_rox()`, `set_direct_map_invalid_noflush()`, `set_direct_map_default_noflush()`, `set_direct_map_valid_noflush()`, `kernel_page_present()`, `can_set_direct_map()`, `set_mce_nospec()`, `clear_mce_nospec()`, `set_memory_encrypted()`, and `set_memory_decrypted()`.

When `CONFIG_ARCH_HAS_SET_MEMORY` is enabled, architecture code from `asm/set_memory.h` supplies the core implementations. Otherwise, the page-permission calls return success without changing mappings. `set_memory_rox()` composes read-only and executable transitions unless an architecture overrides it. Direct-map helpers similarly degrade to no-ops unless `CONFIG_ARCH_HAS_SET_DIRECT_MAP` is present.

## Control Flow

The only implemented flow in this header is sequential composition in `set_memory_rox()`: make pages read-only, return any error, then make them executable. Other inline fallbacks immediately return success or default truth values.

## State And Persistence

Real state changes, when supported, are persistent page-table attribute changes owned by architecture code. This header stores no state. The fallback behavior deliberately preserves call-site buildability on unsupported architectures while not enforcing memory permissions.

## Dependencies And Integration Points

Integration points include module text protection, BPF/JIT or generated code permission transitions, direct-map hardening, memory-failure handling on x86, and encrypted memory support. It depends on architecture configuration and `struct page` declarations from surrounding includes.

## Risks And Test Signals

Risks are assuming permission changes occurred on architectures where these are no-ops, ignoring `__must_check` return values, missing TLB/cache flush semantics in architecture implementations, and calling direct-map changes when `can_set_direct_map()` may be false. Test signals include W^X selftests, module load/unload permission checks, x86 MCE nospec tests, encrypted/decrypted memory tests, and architecture boot tests with unsupported configs to verify fallback build behavior.
