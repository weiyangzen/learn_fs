# sources/distributed-fs/ceph-client/include/drm/intel/reg_bits.h

Purpose: wraps generic kernel bitfield helpers in Intel register-oriented macros with explicit width casts and integer-constant-expression validation.

Important APIs/types/functions: width-specific masks and bits include `REG_GENMASK*` and `REG_BIT*`. Field helpers include `REG_FIELD_PREP8`, `REG_FIELD_PREP16`, `REG_FIELD_PREP`, `REG_FIELD_GET8`, `REG_FIELD_GET`, `REG_FIELD_GET64`, and `REG_FIELD_MAX`. Masked write helpers include `REG_MASKED_FIELD`, `REG_MASKED_FIELD_ENABLE`, and `REG_MASKED_FIELD_DISABLE`.

Control flow: these macros are expanded inside register definitions and register-write values. Prep macros validate mask constness, width, power-of-two field shape, and constant value range with build bugs; runtime values are shifted and masked.

State and persistence: none. They affect how register values are encoded before hardware writes.

Dependencies and integration: depends on `linux/bitfield.h` and `linux/bits.h`. Used throughout Intel DRM MMIO register definitions.

Risks and test signals: incorrect masks should fail compilation when constant. Remaining risks are side effects in macro arguments and misuse of 16-bit masked-field protocol. Test with build coverage, sparse/compile warnings, unit-style constant expression checks, and hardware register write traces.
