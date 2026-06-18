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
