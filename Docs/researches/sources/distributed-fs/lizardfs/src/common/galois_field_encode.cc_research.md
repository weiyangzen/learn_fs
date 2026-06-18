# sources/distributed-fs/lizardfs/src/common/galois_field_encode.cc

Purpose: implements table-driven erasure-code encoding with scalar and optional SIMD variants.

Important APIs/types/functions: `ec_encode_data_default`, target-attributed `ec_encode_data_ssse3`, `ec_encode_data_avx`, optional `ec_encode_data_avx2`, `ec_get_encode_function`, static `gEncodeFunction`, and public `ec_encode_data`.

Control flow: each encoder loops over destination rows, then source columns, applying 32-byte GF coefficient tables by splitting input bytes into low/high nibbles. SIMD variants process 16 or 32 bytes per iteration and fall back to scalar tails. With CPU feature detection, a static function pointer is selected at startup.

State and persistence: static function pointer selected once; no persistence.

Dependencies and integration: depends on GCC vector extensions, `__builtin_cpu_supports`, optional `immintrin.h`, and table layout from `ec_init_tables`. Used by Reed-Solomon encoding/recovery.

Risks: low-level vector casts and target attributes are compiler/architecture sensitive. CPU dispatch is compile-time gated by GCC version and `LIZARDFS_HAVE_CPU_CHECK`. No runtime validation of buffer alignment, lengths, or table sizes.

Test signals: no direct tests here; EC read tests indirectly exercise encoding/decoding paths depending on build configuration.
