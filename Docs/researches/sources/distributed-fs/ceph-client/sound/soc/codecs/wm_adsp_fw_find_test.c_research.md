# sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp_fw_find_test.c

## Purpose

`wm_adsp_fw_find_test.c` is a KUnit suite for the firmware lookup algorithm in `wm_adsp.c`. It validates search order, selected file behavior, firmware-name normalization, all firmware-type stems, and policy combinations involving system name, ALSA prefix, explicit firmware-file name, optional `.wmfw`, and mandatory `.bin`.

## Important APIs, Types, and Functions

- `struct wm_adsp_fw_find_test`: test fixture containing a `struct wm_adsp`, found firmware result, and accumulated searched filename string.
- `struct wm_adsp_fw_find_test_params`: parameter record describing DSP identity inputs, policy flags, expected files, expected search order, and simulated directory contents.
- Static stubs: `wm_adsp_fw_find_test_firmware_request_stub`, `wm_adsp_fw_find_test_firmware_request_simple_stub`, and `wm_adsp_fw_find_test_release_firmware_files_stub` replace real firmware request/release functions.
- Test bodies: `wm_adsp_fw_find_test_search_order`, `wm_adsp_fw_find_test_pick_file`, and `wm_adsp_fw_find_test_find_firmware_byindex`.
- Fixture lifecycle: `wm_adsp_fw_find_test_case_init`, `wm_adsp_fw_find_test_case_exit`, and `wm_adsp_free_found_fw`.
- Parameter arrays: full-search, system+ALSA, system-only, ALSA-only, unqualified, normalization, and pick-file regression cases.

## Control Flow

The fixture allocates a private object, a dummy component to hold `name_prefix`, and a KUnit device assigned to `dsp.cs_dsp.dev`. Search-order tests fill the DSP fields from the current parameter, activate static stubs for firmware request/release, call `wm_adsp_request_firmware_files`, deactivate stubs, and compare the accumulated space-separated search string plus selected file pointers.

Pick-file tests use a simulated directory listing and a simpler request stub that succeeds when the requested filename appears in `dir_files`. They verify which firmware and coefficient filenames are selected for realistic directory contents. The firmware-by-index test iterates `wm_adsp_get_fwf_name_by_index` until NULL and checks that each firmware stem appears in the search string.

## State and Persistence Behavior

The suite stores found filenames in `priv->found_fw` and releases them through a test-specific stub because dummy firmware pointers were not allocated by `request_firmware`. `searched_fw_files` persists for one parameter execution and is reset in the firmware-by-index loop. The tests mutate only the fixture `wm_adsp`, dummy component prefix, and found firmware container.

## Dependencies and Integration Points

The test depends on KUnit device helpers, static stubs, and `CONFIG_KUNIT` exports from `wm_adsp.c`. It directly exercises `wm_adsp_request_firmware_files`, `wm_adsp_get_fwf_name_by_index`, `wm_adsp_firmware_request`, and `wm_adsp_release_firmware_files`.

## Risks and Edge Cases

- Expected search strings are long and exact; harmless formatting changes in the algorithm will fail tests.
- The suite intentionally documents a possible limitation: ALSA-prefix-qualified files are not searched without a system name.
- `bin_mandatory` is represented in pick cases, but the request helper itself mainly returns selected files; enforcement of mandatory `.bin` during power-up still needs separate coverage.
- Directory-pick regression tests are selective and do not prove every possible directory combination.

## Test Signals

The suite itself is the test signal. Passing cases demonstrate preserved search ordering, correct fallback from fully qualified to system-only to legacy to generic files, correct `.bin` matching rules, optional `.wmfw` support, normalization of spaces/underscores/slashes/uppercase/punctuation, no mismatch between filename and firmware pointer presence, and coverage of every known firmware stem.
