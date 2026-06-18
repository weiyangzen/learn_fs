# subset-b-001285 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_control_cache.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_control_cache.c

## Purpose
`cs_dsp_test_control_cache.c` is a slow KUnit regression suite for the Cirrus `cs_dsp` firmware control cache. It builds mock WMFW images with coefficient controls, seeds the mocked DSP regmap with control backing data, powers/runs/stops/swaps firmware, and checks that `struct cs_dsp_coeff_ctl` cache contents are initialized, read, written, and re-applied to hardware registers at the correct time.

The suite covers ADSP2 16-bit, ADSP2 32-bit, and Halo mock DSP layouts, and WMFW format versions 1, 2, and 3. WMFW V1 uses the legacy one-control-per-algorithm-memory shape, while V2/V3 add named multiple controls and extra tests for allocation size and multiple offsets.

## Important APIs, types, and functions
- `struct cs_dsp_test_local` carries the mock XM header, mock WMFW builder, and selected WMFW version for each test.
- `struct cs_dsp_ctl_cache_test_param` parameterizes memory region, algorithm id, word offset, byte length, control type, and WMFW flags.
- `cs_dsp_ctl_cache_test_algs` defines four mock algorithms with distinct ids, versions, base words, and memory sizes across XM/YM/ZM; helpers `_find_alg_entry()` and `_get_alg_mem_base_words()` map test parameters to backing addresses.
- `_create_dummy_wmfw()` creates a WMFW builder and inserts the mandatory XM header data block.
- Cache initialization tests include `cs_dsp_ctl_v2_cache_alloc()`, `cs_dsp_ctl_cache_init()`, `cs_dsp_ctl_cache_init_write_only()`, `cs_dsp_ctl_cache_init_multiple_fw_same_controls()`, `cs_dsp_ctl_cache_init_multiple_fwalgid_same_controls()`, `cs_dsp_ctl_cache_init_multiple_mems()`, `cs_dsp_ctl_cache_init_multiple_algs()`, and `cs_dsp_ctl_cache_init_multiple_offsets()`.
- Read tests include `cs_dsp_ctl_cache_read_not_started()`, `cs_dsp_ctl_cache_read_stopped()`, `cs_dsp_ctl_cache_read_powered_down()`, `cs_dsp_ctl_cache_read_stopped_powered_down()`, `cs_dsp_ctl_cache_read_not_current_loaded_fw()`, `cs_dsp_ctl_cache_read_not_current_running_fw()`, `cs_dsp_ctl_cache_read_running()`, and `cs_dsp_ctl_cache_read_running_zero_flags()`.
- Write tests include `cs_dsp_ctl_cache_writethrough()`, `cs_dsp_ctl_cache_writethrough_unchanged()`, `cs_dsp_ctl_cache_write_unchanged_not_started()`, `cs_dsp_ctl_cache_write_not_started()`, `cs_dsp_ctl_cache_write_stopped()`, `cs_dsp_ctl_cache_write_powered_down()`, `cs_dsp_ctl_cache_write_stopped_powered_down()`, `cs_dsp_ctl_cache_write_not_current_loaded_fw()`, and `cs_dsp_ctl_cache_write_not_current_running_fw()`.
- Sync/reapply tests include `cs_dsp_ctl_cache_sync_write_before_run()`, `cs_dsp_ctl_cache_sync_write_while_running()`, `cs_dsp_ctl_cache_sync_write_after_stop()`, `cs_dsp_ctl_cache_sync_write_not_current_fw()`, `cs_dsp_ctl_cache_sync_reapply_every_run()`, `cs_dsp_ctl_cache_sync_reapply_after_fw_reload()`, and `cs_dsp_ctl_cache_sync_reapply_after_fw_swap()`.
- Test setup uses `cs_dsp_ctl_cache_test_common_init()` plus Halo/ADSP2-specific initializers, then registers five suites through `kunit_test_suites()`.

## Control flow
Each test allocates a mock `struct cs_dsp`, registers a dummy KUnit device, initializes the mock regmap, creates an XM header with the suite's algorithm table, builds a WMFW image, and initializes the DSP through `cs_dsp_adsp2_init()` or `cs_dsp_halo_init()`. Cleanup is action-based: device references, `cs_dsp_stop()`, and `cs_dsp_remove()` are registered with KUnit wrappers where needed.

The common test pattern is: compute a backing register from memory base plus algorithm base plus control offset, write initial bytes into the mock regmap, add one or more coefficient descriptors to a WMFW algorithm-info block, call `cs_dsp_power_up()`, optionally call `cs_dsp_run()`, stop or power down, then read/write the resulting `struct cs_dsp_coeff_ctl`. The tests compare `cs_dsp_coeff_lock_and_read_ctrl()` results against the expected cache bytes and compare regmap reads or mock dirty state to decide whether hardware was touched.

The multiple-firmware paths create separate builders for firmware names such as `misc`, `mbc/vss`, and `haps`. They deliberately load, run, stop, and power down several images so that the same logical control can exist under different firmware names, algorithm ids, memory regions, or offsets. The suite avoids assuming `dsp->ctl_list` order and locates controls by `fw_name`, `alg_region.alg`, `alg_region.type`, or `offset`.

## State and persistence behavior
The state under test is runtime-only kernel state: `dsp->ctl_list`, `struct cs_dsp_coeff_ctl::cache`, `len`, `flags`, `enabled`, `set`, `offset`, `fw_name`, and `alg_region`. Cache contents persist across firmware stop, DSP power-down, firmware reload, and firmware swaps as long as the control object remains on the DSP control list. For non-current firmware, writes update only the stored cache and mark state for later synchronization, not the active registers.

Non-volatile readable controls initialize their cache from backing registers at firmware download. Non-volatile write-only controls initialize to zeros because the register value cannot be read. While firmware is running, normal cached controls read from the cache; old controls with `flags == 0` intentionally behave as volatile for backwards compatibility and read live registers while running. Writes to running/current controls are write-through to cache and registers, while writes before run, after stop, after power-down, or to controls from another firmware stay cache-only until the relevant firmware is run again.

## Dependencies and integration points
The suite depends on KUnit, `kunit/device`, KUnit resources/actions, `regmap_raw_read()`/`regmap_raw_write()`, `get_random_bytes()`, and the Cirrus mock helpers in `cs_dsp_test_utils.h`. It integrates directly with the public/internal `cs_dsp` lifecycle and control APIs: `cs_dsp_power_up()`, `cs_dsp_run()`, `cs_dsp_stop()`, `cs_dsp_power_down()`, `cs_dsp_remove()`, `cs_dsp_adsp2_init()`, `cs_dsp_halo_init()`, `cs_dsp_coeff_lock_and_read_ctrl()`, and `cs_dsp_coeff_lock_and_write_ctrl()`.

Mock WMFW builders and XM headers provide the firmware parsing input, while mock memory-region helpers abstract ADSP2 16-bit, ADSP2 32-bit, and Halo address increments. ZM-specific cases are included where the mock DSP exposes ZM; WMFW V3/Halo omits the explicit Z-only parameter cases because Halo memory support differs from the ADSP2 V1/V2 suites.

## Risks and edge cases
Key risk areas are stale cache data being overwritten on firmware reload, writes leaking to registers for disabled or non-current controls, register reads occurring when a cached read should be sufficient, and failing to reapply cached writes on every future run. The tests also target identity collisions between controls with the same descriptor fields but different firmware, algorithm id, memory type, or offset.

The suite is sensitive to control flags. `flags == 0` has special legacy volatile behavior; write-only controls are zero-initialized and make the first same-value write look like a change if the existing cache was zero rather than the seeded register value. The mock dirty-state checks protect against accidental regmap access but require the tests to drop expected XM-header and control-register writes from the mock cache before assertions.

Coverage differs by WMFW version. V2/V3 can test multiple controls in one algorithm at different offsets and cache allocation sizes; V1 cannot represent those cases. Any future change to the WMFW descriptor layout, cache allocation strategy, or control uniqueness criteria should be checked against these suite splits.

## Test signals
Passing signals are successful registration and execution of the five slow KUnit suites: `cs_dsp_ctl_cache_wmfwV3_halo`, `cs_dsp_ctl_cache_wmfwV1_adsp2_32bit`, `cs_dsp_ctl_cache_wmfwV2_adsp2_32bit`, `cs_dsp_ctl_cache_wmfwV1_adsp2_16bit`, and `cs_dsp_ctl_cache_wmfwV2_adsp2_16bit`.

High-value assertions include `list_count_nodes(&dsp->ctl_list)` for control identity, `ksize(ctl->cache) >= ctl->len` for V2 allocation, `KUNIT_EXPECT_MEMEQ()` between cache reads and seeded/random values, `KUNIT_EXPECT_MEMNEQ()` before deferred sync, regmap readback equality after run-time write-through or reapply, and `cs_dsp_mock_regmap_is_dirty(priv, true) == false` when cache-only reads/writes should not touch registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_control_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_control_parse.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_test_control_parse.c -->
