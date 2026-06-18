<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc64.h -->
# sources/distributed-fs/ceph/src/rgw/spdk/crc64.h

Purpose: Declares the SPDK CRC-64 NVMe checksum API.

Important APIs, types, and functions: Exposes C-linkage `uint64_t spdk_crc64_nvme(const void *buf, size_t len, uint64_t crc)`.

Control flow: C and C++ callers include this header and pass a buffer, length, and previous CRC seed for one-shot or incremental checksum calculation.

State and persistence: No state or persistence.

Dependencies and integration points: Includes standard integer and size types directly in this Ceph copy, with original SPDK config includes disabled by `#if 0`. Used by `crc64.c` and any RGW checksum callers.

Risks and test signals: API compatibility with upstream SPDK matters. Compile tests should include both C and C++ callers; checksum tests should validate incremental use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc64.h -->
