# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_wmfw_error.c

## Purpose
This is the negative-path KUnit suite for Cirrus `cs_dsp` WMFW parsing. It mutates valid synthetic firmware into malformed files and checks that `cs_dsp_power_up()` rejects unsafe inputs or safely tolerates explicitly supported cases.

## Important APIs, Types, And Functions
`struct cs_dsp_test_local` stores the mock XM header, WMFW builder, and version. Setup pre-populates the XM header into the mock regmap so malformed WMFW files do not need an XM blob. `struct cs_dsp_wmfw_test_param` parameterizes raw block type.

Important tests cover unknown-block skipping, wrong magic, too-short top-level headers, bad header length, bad core type, truncated block headers/payloads, garbage block lengths, truncated algorithm headers, V1 fixed-name and coefficient-count issues, and V2/V3 variable-length algorithm and coefficient metadata overflows.

## Control Flow
Most cases generate valid firmware, sanity-check that it loads, power down, mutate the firmware bytes, and call `cs_dsp_power_up()` expecting failure, commonly `-EOVERFLOW`. Header tests mutate `struct wmfw_header`; block tests mutate `struct wmfw_region`; algorithm and coefficient tests cast the region payload to V1 fixed structs or V2+ `__le32` layouts and alter count or length fields.

Version-specific case arrays choose v0, v1, v2, or v3 parser expectations. HALO uses WMFW v3 and HALO-valid block types; ADSP2 suites run 16-bit/32-bit variants across WMFW v0-v2.

## State And Persistence Behavior
State is KUnit-scoped. A valid sanity load can change DSP state, so cases power down before testing mutated firmware. Unknown blocks are expected to be skipped while later valid payloads still load. Unterminated V1 names are expected not to overread and can still produce controls because those names are parsed but not stored.

## Dependencies And Integration Points
The suite depends on KUnit, static stubs, regmap, random helpers, vmalloc, Cirrus DSP/WMFW headers, and `cs_dsp_test_utils.h`. It is tightly coupled to binary layouts in `wmfw.h` and to `cs_dsp_power_up()` parser behavior.

## Risks And Edge Cases
Covered risks include parser overread, integer overflow, malformed length acceptance, wrong core type acceptance, and unsafe string length handling. Boundary values include `0x7fffffff`, `0x80000000`, `0xffffffff`, maximum byte-sized names, and maximum 16-bit descriptions. Repeated invalid-block cases call the block-header truncation test, which narrows signal for invalid block payload-length behavior.

## Test Signals
Passing tests indicate malformed WMFW files fail closed, unknown-block skipping still works, legacy unterminated strings do not overrun, and V2/V3 variable metadata remains bounded by containing blocks.
