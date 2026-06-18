# sources/distributed-fs/ceph-client/drivers/net/ipa/reg.h

Purpose: Provides the common descriptor format and helper macros/functions for versioned IPA and GSI register maps.

Important APIs and types: `struct reg` describes a register offset, instance stride, field-mask array, and name. `struct regs` wraps a version-specific array of register descriptors. Macros `REG`, `REG_STRIDE`, `REG_FIELDS`, and `REG_STRIDE_FIELDS` define static register descriptors. Inline helpers `reg()`, `reg_fmask()`, `reg_bit()`, `reg_field_max()`, `reg_encode()`, `reg_decode()`, `reg_offset()`, and `reg_n_offset()` implement validated access to offsets and bitfields.

Control flow: Callers select a `struct reg` by register ID, optionally encode/decode fields using mask arrays, and compute either a simple offset or an indexed offset using stride. Error cases warn and return zero or NULL-like fallbacks, allowing caller paths to avoid immediate crashes while surfacing invalid register IDs or field IDs.

State and persistence: No mutable state exists. The descriptors are static constants, and their values encode the hardware ABI for all register accesses.

Dependencies and integration points: Used by `ipa_reg()` and `gsi_reg()` wrappers and every versioned file in `drivers/net/ipa/reg/`. It depends on Linux `ARRAY_SIZE`, bit, bug, log2, and type helpers.

Risks: `reg_bit()` assumes the field mask is a single bit; using it for multi-bit fields warns and returns zero. `reg_encode()` silently returns zero on invalid values after warning, which can accidentally program a zero field if callers ignore validation. Offset zero is both a possible fallback and a legitimate value in some v5 IPA maps, so callers should not treat zero offset alone as success.

Test signals: Compile all versioned register maps; unit-like checks for encode/decode boundaries; runtime probe on each supported hardware version; fault-injection or debug coverage for out-of-range register/field IDs.
