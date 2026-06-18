# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_control_parse.c

## Purpose
`cs_dsp_test_control_parse.c` is a slow KUnit regression suite for parsing Cirrus `cs_dsp` coefficient controls from mock WMFW algorithm-info blocks. It verifies descriptor string handling, field extraction, type/flag validation, control lookup, uniqueness, and duplicate suppression across WMFW versions and mock DSP families.

The suite is explicitly split by firmware format. WMFW V1 controls have no usable parsed names, so V1 tests prove that descriptor name fields are ignored. WMFW V2/V3 tests prove that short names are used, full names and descriptions are skipped correctly, variable-length fields are padded correctly, and multiple named controls can coexist in one algorithm.

## Important APIs, types, and functions
- `struct cs_dsp_test_local` stores the mock XM header, WMFW builder, and selected WMFW version.
- `struct cs_dsp_ctl_parse_test_param` parameterizes memory type, algorithm id, offset, length, control type, and flags.
- `cs_dsp_ctl_parse_test_algs` supplies four mock algorithms with ids `0xfafa`, `0xb`, `0x9f1234`, and `0xff00ff`; each has XM/YM/ZM sizes for descriptor-boundary testing.
- `mock_coeff_template` is the base coefficient descriptor: short name `"Dummy Coeff"`, bytes type, YM memory, volatile flag, and 4-byte length.
- Name/string parsing tests include `cs_dsp_ctl_parse_v1_name()`, `cs_dsp_ctl_parse_empty_v1_name()`, `cs_dsp_ctl_parse_max_v1_name()`, `cs_dsp_ctl_parse_short_name()`, `cs_dsp_ctl_parse_min_short_name()`, `cs_dsp_ctl_parse_max_short_name()`, `cs_dsp_ctl_parse_with_min_fullname()`, `cs_dsp_ctl_parse_with_max_fullname()`, `cs_dsp_ctl_parse_with_min_description()`, `cs_dsp_ctl_parse_with_max_description()`, and `cs_dsp_ctl_parse_with_max_fullname_and_description()`.
- Alignment and lookup tests include `cs_dsp_ctl_shortname_alignment()`, `cs_dsp_ctl_fullname_alignment()`, `cs_dsp_ctl_description_alignment()`, `cs_dsp_get_ctl_test()`, `cs_dsp_get_ctl_test_multiple_wmfw()`, and `cs_dsp_ctl_v2_compare_len()`.
- Field and validation tests include `cs_dsp_ctl_parse_memory_type()`, `cs_dsp_ctl_parse_alg_id()`, `cs_dsp_ctl_parse_alg_mem()`, `cs_dsp_ctl_parse_offset()`, `cs_dsp_ctl_parse_length()`, `cs_dsp_ctl_parse_ctl_type()`, `cs_dsp_ctl_parse_flags()`, and `cs_dsp_ctl_illegal_type_flags()`.
- Identity tests include `cs_dsp_ctl_parse_fw_name()`, `cs_dsp_ctl_alg_id_uniqueness()`, `cs_dsp_ctl_mem_uniqueness()`, `cs_dsp_ctl_fw_uniqueness()`, `cs_dsp_ctl_squash_reloaded_controls()`, and `cs_dsp_ctl_v2_squash_reloaded_controls()`.
- Test setup is handled by `cs_dsp_ctl_parse_test_common_init()` and DSP-specific init wrappers, with five suites registered through `kunit_test_suites()`.

## Control flow
Setup allocates a KUnit-owned `struct cs_dsp_test`, local state, and mock `struct cs_dsp`; registers a dummy device; initializes a mock regmap; creates an XM header containing the mock algorithms; creates a WMFW builder for the requested format version; inserts the XM header as a WMFW data block; then initializes the DSP as ADSP2 or Halo. KUnit actions release the device and remove the DSP at teardown.

Individual tests create one or more algorithm-info blocks, add coefficient descriptors with selected fields, finalize the mock firmware with `cs_dsp_mock_wmfw_get_firmware()`, and call `cs_dsp_power_up()`. They then inspect the first control in `dsp->ctl_list`, walk the full list, or call `cs_dsp_get_ctl()` under `dsp->pwr_lock` to validate lookup behavior. Multi-firmware tests power down and load a second WMFW builder so current-firmware filtering and `fw_name` qualification can be tested.

The parameter generators sweep memory types, algorithm ids, offsets, lengths, legal type/flag tuples, standalone flags, and illegal type/flag tuples. Illegal descriptors are expected to make `cs_dsp_power_up()` fail, while legal descriptors are expected to produce a populated `struct cs_dsp_coeff_ctl` with parsed fields matching the descriptor or parent algorithm block.

## State and persistence behavior
The suite validates runtime `cs_dsp` state rather than persistent storage. Parsed controls are stored on `dsp->ctl_list` as `struct cs_dsp_coeff_ctl` objects. Important fields are `subname`, `subname_len`, `alg_region.alg`, `alg_region.type`, `offset`, `type`, `flags`, `len`, and `fw_name`.

Controls persist on the list after `cs_dsp_power_down()`. Reloading the same WMFW must not duplicate controls; the duplicate-squash tests take pointer snapshots and require the same objects to remain after reload. Loading a different firmware with an otherwise identical control must create a separate object distinguished by `fw_name`, and `cs_dsp_get_ctl()` should resolve the matching control for the currently loaded firmware.

## Dependencies and integration points
The file depends on KUnit, KUnit devices/resources, mutex locking, list helpers, regmap, Cirrus mock WMFW/XM-header utilities, and WMFW constants for memory regions, control types, and flags. It integrates with `cs_dsp_power_up()`, `cs_dsp_power_down()`, `cs_dsp_remove()`, `cs_dsp_get_ctl()`, `cs_dsp_adsp2_init()`, and `cs_dsp_halo_init()`.

The same source exercises multiple hardware abstractions: Halo with WMFW V3, ADSP2 32-bit with WMFW V1/V2, and ADSP2 16-bit with WMFW V1/V2. ZM parameter cases return early when the selected mock DSP has no ZM memory, avoiding permanent KUnit skip state while still covering ZM where available.

## Risks and edge cases
String parsing is a major risk. WMFW V2/V3 coefficient descriptors contain variable-length short name, full name, and description fields padded to 4-byte boundaries; incorrect padding would shift later fields and corrupt flags, type, or length. The suite tests lengths from 1 to 15, 255-byte names, 65535-byte descriptions, and full-name/description combinations. It also covers a previous short-name comparison bug by ensuring names such as `LEFT`, `LEFT_`, `LEFT2`, and longer `LEFT_SPK*` variants are compared by full length, not shortest-prefix length.

Control identity is another risk. Controls that are identical except algorithm id, memory region, or firmware name must coexist, while reloading the same firmware must not create duplicates. `cs_dsp_get_ctl()` must filter by current firmware as well as name, memory type, and algorithm id.

Type and flag validation is deliberately strict for special controls. ACKED controls must be volatile, readable, and writeable; HOSTEVENT and FWEVENT must also be system controls; HOST_BUFFER must be system, volatile, and readable, with writeable optional. The illegal matrix ensures unsupported combinations fail during firmware parse rather than creating unusable controls.

## Test signals
Passing signals are successful execution of `cs_dsp_ctl_parse_wmfwV3_halo`, `cs_dsp_ctl_parse_wmfwV1_adsp2_32bit`, `cs_dsp_ctl_parse_wmfwV2_adsp2_32bit`, `cs_dsp_ctl_parse_wmfwV1_adsp2_16bit`, and `cs_dsp_ctl_parse_wmfwV2_adsp2_16bit`.

Important assertions include `subname_len == 0` for V1 name fields, exact `subname` memory equality for V2/V3 short names, unchanged parsed `flags`/`type`/`len` after variable-length fields, correct `alg_region` and `offset` for parameter cases, negative `cs_dsp_power_up()` for illegal type/flag descriptors, `list_count_nodes()` for uniqueness and duplicate suppression, and pointer equality when a WMFW is reloaded.
