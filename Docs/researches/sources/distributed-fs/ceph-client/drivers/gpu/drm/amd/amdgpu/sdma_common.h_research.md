# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_common.h

Purpose: provides shared SDMA UTCL2 cache read/write policy enum values for SDMA packet emission code.

Important APIs/types/functions: defines `enum sdma_utcl2_cache_read_policy` with LRU, STREAM, NOA, and default NOA values; defines `enum sdma_utcl2_cache_write_policy` with LRU, STREAM, NOA, BYPASS, and default BYPASS values.

Control flow: no runtime control flow. Packet emitters select these values when programming SDMA packet cache-policy fields.

State and persistence behavior: no state. Values persist only in emitted command streams and hardware cache behavior.

Dependencies and integration points: included by SDMA generation implementations and packet-building helpers that need a common policy vocabulary across ASIC versions.

Risks and test signals: risks are mismatched enum values with hardware packet definitions or using defaults inappropriate for a given engine generation. Test signals include SDMA copy/fill/PTE operations under cache-coherency stress, VM update correctness, and performance/ordering validation with different cache policies.
