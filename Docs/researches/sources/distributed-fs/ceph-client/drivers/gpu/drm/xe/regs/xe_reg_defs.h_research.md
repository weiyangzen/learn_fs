# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_reg_defs.h

## Purpose

`xe_reg_defs.h` defines the typed register representation used across the Xe driver. It wraps MMIO offsets plus access metadata in `struct xe_reg`, provides `struct xe_reg_mcr` for multicast/replicated registers, and supplies `XE_REG()`, `XE_REG_MCR()`, and related options.

## Important APIs, Types, and Definitions

- `XE_REG_ADDR_MAX` sets the encoded register offset limit to 4 MiB.
- `struct xe_reg` stores `addr`, `masked`, `mcr`, and `vf` fields in a 32-bit union with a `raw` representation.
- `struct xe_reg_mcr` wraps a `struct xe_reg` to enforce MCR-specific APIs by type.
- Options: `XE_REG_OPTION_MASKED` and `XE_REG_OPTION_VF`.
- Constructors: `XE_REG_INITIALIZER`, `XE_REG`, and `XE_REG_MCR`.
- `xe_reg_is_valid()` treats address zero as invalid.

## Control Flow

Only `xe_reg_is_valid()` has local executable logic. Other definitions are compile-time initializers that produce typed register constants for MMIO helpers, save/restore tables, RTP workarounds, tests, and validation code.

## State and Persistence Behavior

The file defines software metadata, not hardware state. The metadata persists in constants and tables and controls access behavior: masked write handling, MCR routing, and VF-access validation.

## Dependencies and Integration Points

It depends on DRM Intel `pick.h` and `reg_bits.h`, plus Linux build/log2/size helpers. It is foundational to nearly every Xe register header, MMIO path, workaround table, RTP tests, save/restore state, and SR-IOV VF register access checks.

## Risks and Edge Cases

- Address bit width is derived from `XE_REG_ADDR_MAX`; increasing the supported MMIO range requires validating bitfield packing and static assertions.
- Address zero is invalid by convention, so a real register at offset zero cannot be represented as valid by `xe_reg_is_valid()`.
- `XE_REG_MCR()` sets `.mcr = 1`; using `XE_REG()` for an MCR register can route access through the wrong path.
- Masked-register semantics require consumers to respect upper-16-bit write masks.

## Test Signals

`xe_rtp_test.c` exercises regular, masked, and MCR register metadata interactions. Compile coverage checks the 32-bit layout. Useful additional tests include constructor raw-value checks, invalid-zero behavior, VF option propagation, and MCR type separation.
