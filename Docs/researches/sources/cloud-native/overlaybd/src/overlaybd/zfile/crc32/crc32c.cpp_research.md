# sources/cloud-native/overlaybd/src/overlaybd/zfile/crc32/crc32c.cpp

Purpose: CRC32C implementation with software fallback, hardware CPU instructions, and optional Intel DSA or ISA-L accelerated paths.

Important APIs/types/functions: exported functions are `crc32c`, `crc32c_extend`, string overloads, and testing helpers `crc32c_slow` / `crc32c_fast`. Internal implementations include `crc32c_hw`, `singletable_crc32c`, slicing-by-8 table logic via `crc32c_sb8_64_bit` and `multitable_crc32c`, `crc32c_sw`, optional `crc32c_dml`, optional `crc32c_isal`, `check_dsa`, and constructor/destructor hooks `crc_init` / `crc_deinit`.

Control flow: at library load, `crc_init` selects the global function pointer. On x86 with SSE4.2 it optionally prefers DSA, then ISA-L AVX512, then SSE4.2 instructions, otherwise software; on ARM with CRC32 it uses mapped builtins; other platforms use software. Public calls dispatch through `crc32c_func` with an initial or caller-supplied CRC seed.

State and persistence: the only state is process-global `crc32c_func`, initialized once by constructor. CRC values are used by zfile integrity paths but this file does not persist data directly.

Dependencies/integration: linked as `crc32_lib`, consumed by zfile. Depends on compiler intrinsics, Photon logging, optional DML high-level API, optional libpci device probing, and optional ISA-L `crc32_iscsi`.

Risks: public functions assume `crc_init` ran and `crc32c_func` is non-null. `multitable_crc32c` computes `to_even_word` as 4 when already aligned, so short lengths under 4 are routed away but other edge cases depend on table helper assumptions. Optional DSA detection scans PCI devices at constructor time, which can be slow or permission-sensitive. Testing helper `crc32c_fast` calls hardware instructions unconditionally, so it is only safe on builds/CPUs with the required feature.

Test signals: testing namespace exposes slow and fast implementations for cross-checking. Build flags in CMake add architecture options and optional accelerator definitions; zfile tests should validate checksums across block boundaries and extension seeds.
