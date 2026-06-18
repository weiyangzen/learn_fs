# sources/distributed-fs/ceph-client/arch/x86/include/asm/mtrr.h

## Purpose
Defines x86 Memory Type Range Register hardware masks, saved-state structure, runtime APIs, fallback stubs, and 32-bit compat ioctl layouts.

## Important APIs, Types, And Functions
Defines masks for `MTRR_CAP`, default type, `PHYSBASE`, and `PHYSMASK`, plus `struct mtrr_state_type`. Runtime APIs under `CONFIG_MTRR` include `mtrr_bp_init()`, `guest_force_mtrr_state()`, `mtrr_type_lookup()`, `mtrr_save_fixed_ranges()`, `mtrr_save_state()`, `mtrr_add()`, `mtrr_add_page()`, `mtrr_del()`, `mtrr_del_page()`, `mtrr_trim_uncached_memory()`, `amd_special_default_mtrr()`, `mtrr_disable()`, `mtrr_enable()`, and `mtrr_generic_set_state()`. Compat structs and `MTRRIOC32_*` ioctl numbers support 32-bit userspace.

## Control Flow
Callers add/delete MTRR ranges, save/restore fixed ranges, look up effective type over an address range, and temporarily disable/enable MTRRs during updates. Disabled configs return uncachable defaults or `-ENODEV`.

## State And Persistence
State includes hardware MTRR MSRs and saved kernel copies in `mtrr_state_type`. Hardware state persists until changed or reset.

## Dependencies And Integration Points
Depends on UAPI MTRR types and Linux bits. It integrates with PAT, cacheability selection, KVM guest MTRR emulation, `/proc/mtrr` ioctls, and early memory trimming.

## Risks And Edge Cases
MTRR changes affect cache coherency globally. Range alignment, fixed vs variable ranges, and default types are hardware-sensitive. Compat ioctl layouts must stay ABI-stable.

## Test Signals
MTRR ioctl tests, PAT/MTRR cache-type tests, KVM guest MTRR tests, AMD default MTRR quirks, and disabled-config builds are useful.
