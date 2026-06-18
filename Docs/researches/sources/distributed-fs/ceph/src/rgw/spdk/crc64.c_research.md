<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc64.c -->
# sources/distributed-fs/ceph/src/rgw/spdk/crc64.c

Purpose: Provides SPDK-compatible CRC-64 Rocksoft/NVMe checksum implementation for RGW.

Important APIs, types, and functions: Public `spdk_crc64_nvme(const void *buf, size_t len, uint64_t crc)` is implemented either by ISA-L `crc64_rocksoft_refl()` when `SPDK_CONFIG_ISAL` is defined or by local table-driven fallback. The fallback uses `crc64_rocksoft_refl_table[256]` and `crc64_rocksoft_refl_base()`.

Control flow: Compile-time configuration selects ISA-L or fallback. Fallback complements the seed, iterates bytes, updates CRC using table lookup of low CRC byte xor input byte and right shift, then returns complemented CRC.

State and persistence: The only state is a static constant lookup table. No persistence.

Dependencies and integration points: Depends on `crc_internal.h`, `crc64.h`, optional ISA-L `crc64.h`, and standard integer types. Used by RGW code needing NVMe protection information CRC compatibility.

Risks and test signals: Hardware/library and fallback paths must produce identical output. Tests should include known CRC-64 Rocksoft vectors, incremental CRC updates, empty buffers, unaligned buffers, and builds with and without ISA-L.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc64.c -->
