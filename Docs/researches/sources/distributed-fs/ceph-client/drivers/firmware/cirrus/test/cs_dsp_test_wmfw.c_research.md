# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_wmfw.c

## Purpose
This is the positive-path KUnit suite for loading WMFW firmware data into the Cirrus `cs_dsp` mock regmap. It verifies that `cs_dsp_power_up()` parses synthetic firmware and writes payloads to expected DSP memory addresses for ADSP2 and HALO devices.

## Important APIs, Types, And Functions
`struct cs_dsp_test_local` stores the synthetic XM header, WMFW builder, and version. `struct cs_dsp_wmfw_test_param` parameterizes memory type and block count. The test functions cover mandatory XM header writes, single and multiple payloads, reverse and sparse unordered payloads, full PM region downloads, mixed unpacked memory, mixed HALO packed/unpacked memory, packed/unpacked boundary cases, and info text blocks.

`cs_dsp_wmfw_test_common_init()` allocates KUnit state, registers a test device, initializes the mock regmap, builds and adds the XM header block, initializes ADSP2 or HALO DSP ops, registers cleanup, and stubs `cs_dsp_can_emit_message()` to reduce log noise.

## Control Flow
Tests add WMFW data or info blocks through the mock builder, obtain a `struct firmware`, call `cs_dsp_power_up()`, compute expected regmap addresses from memory base, stride, packed/unpacked block size, and DSP-word offset, read back bytes, compare them to random payloads, drop expected cache entries, and assert the regmap cache is clean.

The suite runs HALO WMFW v3 and ADSP2 16-bit/32-bit WMFW v0/v1/v2 variants. Parameter tables cover PM, XM, YM, ZM for ADSP2 and packed PM/XM/YM plus unpacked XM/YM for HALO.

## State And Persistence Behavior
All state is per-test. Large PM payload buffers use `vmalloc()` with KUnit cleanup. The important persistence signal is mock regmap cache contents after firmware download: once expected writes and the XM header are dropped, the cache should be clean.

## Dependencies And Integration Points
The file depends on KUnit, static stubs, regmap, random data, vmalloc, Cirrus `cs_dsp` core headers, WMFW definitions, and `cs_dsp_test_utils.h`. It exercises the real firmware power-up path using mock DSP region metadata.

## Risks And Edge Cases
The highest-risk area is address translation, especially for HALO packed memories and mixed packed/unpacked blocks. The suite stresses unordered blocks, sparse placement, full-region PM writes, block-count boundaries, and avoiding collisions with the mandatory XM header.

## Test Signals
Passing tests indicate positive WMFW loading writes payloads exactly where expected, tolerates info blocks, handles HALO packed data, and performs no unexpected regmap writes.
