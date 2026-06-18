# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_20_comp_defs.h

## Purpose
`icp_qat_hw_20_comp_defs.h` lists generation 2.0 compression/decompression CSR bit positions, masks, enum values, and defaults used by the generation 2.0 builders.

## Important APIs, Types, And Functions
The file defines enums and defaults for compression SCB, RMB, SOM, skip-hash-read, SCB unload, token fusion, long buffer size, reset mask, lazy/nice parameters, history buffer size, ABD, LLLBD, search depth, compression format, min-match, hash collision/update, byte-skip, and extended delay match. Decompression definitions cover speculative decoder, mini-CAM, history buffer size, long buffer size, format, min-match, and LZ4 block checksum.

## Control Flow
There is no executable control flow. The defs are consumed by `icp_qat_hw_20_comp.h` builder functions and by callers selecting per-algorithm settings.

## State And Persistence Behavior
No state is owned here. The constants define firmware/hardware descriptor semantics and act as a stable hardware contract.

## Dependencies And Integration Points
This header is included by `icp_qat_hw_20_comp.h`. It integrates with device-specific compression context construction for deflate, LZ4, LZ4S, and QAT 2.3 zstd formats.

## Risks
Many enum values are not monotonic defaults from zero, so zero-initialized config structs may not be semantically correct for every field. Format definitions include 2.3 zstd values inside the 2.0 header family, so caller capability checks must select formats only on supporting hardware. Bit masks are raw numeric constants and must match hardware documentation.

## Test Signals
Static review can compare defaults against hardware spec. Runtime compression tests per format and search-depth level validate that selected enum combinations are accepted by firmware.
