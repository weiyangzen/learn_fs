# sources/distributed-fs/lizardfs/src/common/galois_coeff.h

Purpose: builds compile-time GF(2^8) logarithm and exponent lookup tables for erasure coding.

Important APIs/types/functions: `detail::gf_mul2`, recursive constexpr `gf_log` and `gf_exp`, `get_gf_log_table`, `get_gf_exp_table`, and global constexpr arrays `gf_log_table` and `gf_exp_table`.

Control flow: template expansion over `make_index_sequence<255>()` evaluates finite-field powers at compile time. `gf_mul2` uses polynomial reduction with `0x1d`.

State and persistence: global constexpr arrays with static storage; no runtime mutation or persistence.

Dependencies and integration: depends on `integer_sequence.h` and `<array>`. Used by `galois_field_isal.cc` for multiplication/inversion.

Risks: recursive constexpr functions assume valid nonzero/log inputs and would recurse indefinitely for invalid values if called improperly at compile time. The field polynomial must match the rest of the Reed-Solomon implementation.

Test signals: no direct test in subset, but EC read tests exercise downstream Reed-Solomon behavior.
