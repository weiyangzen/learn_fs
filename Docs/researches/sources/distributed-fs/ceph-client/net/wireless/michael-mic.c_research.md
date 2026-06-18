# sources/distributed-fs/ceph-client/net/wireless/michael-mic.c

## Purpose
This file implements the TKIP Michael MIC algorithm used for IEEE 802.11 data integrity compatibility.

## Important APIs, types, and functions
`struct michael_mic_ctx` stores the two 32-bit state words. `michael_block()` applies the Michael mixing function over one little-endian 32-bit word. `michael_mic_hdr()` initializes the context from the 8-byte key and folds in the pseudo-header: destination address, source address, QoS TID or zero, and padding. `michael_mic()` processes payload blocks, appends the 0x5a padding block and final zero block, and writes the 8-byte MIC.

## Control flow
The exported function initializes header state, processes each full 4-byte payload block, constructs the partial tail block in Michael padding order, mixes the tail and zero block, then emits little-endian `l` and `r`.

## State and persistence
All state is stack-local. The function reads the key, header, and payload and writes the caller-provided MIC buffer. No persistent state exists.

## Dependencies and integration points
It depends on IEEE 802.11 header helpers, unaligned little-endian accessors, and bit rotations. It is exported with `EXPORT_SYMBOL_GPL` for wireless encryption/TKIP users.

## Risks
Michael MIC is cryptographically weak but required for TKIP compatibility. Correct byte ordering and padding are essential for interoperability. Callers must supply valid key, header, data, and output buffers.

## Test signals
Use known TKIP Michael MIC test vectors, QoS and non-QoS frames, payload lengths 0 through multiple block boundaries, unaligned data buffers, and endian-sensitive checks.
