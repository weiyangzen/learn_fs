# Research: subset-b-003754

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_hdmi_state_helper_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_hdmi_state_helper_test.c

## Purpose
KUnit coverage for the DRM HDMI connector state helpers. The file builds a mock atomic DRM pipeline with one primary plane, one CRTC, one TMDS encoder, and one HDMI connector, then verifies HDMI atomic check, reset defaults, mode validation, and InfoFrame programming behavior across DVI, HDMI, RGB, YUV, deep-color, HDR, and constrained-TMDS scenarios.

## Important APIs, Types, And Functions
The central fixture is `struct drm_atomic_helper_connector_hdmi_priv`, embedding `struct drm_device`, `drm_encoder`, `drm_connector`, current EDID storage, and an `hdmi_update_failures` counter. `__connector_hdmi_init()` allocates the KUnit device/DRM device, creates a primary plane and CRTC through `drm_kunit_helpers`, initializes an HDMI connector with `drmm_connector_hdmi_init()`, attaches the encoder, resets mode config, and optionally loads EDID. `dummy_connector_get_modes()` turns the current raw EDID into `display_info` and connector modes through `drm_edid_connector_update()` and `drm_edid_connector_add_modes()`. `test_encoder_atomic_enable()` exercises `drm_atomic_helper_connector_hdmi_update_infoframes()`.

## Control Flow
Most tests initialize the fixture with driver-supported output formats and a max BPC, find a preferred or CEA VIC mode, enable the connector with `drm_kunit_helper_enable_crtc_connector()`, then allocate an atomic state and run `drm_atomic_check_only()` or `drm_atomic_commit()`. Repeated `retry_*` labels handle `-EDEADLK` by clearing/backing off the modeset context. Check-suite cases validate broadcast RGB mode-change propagation and quantization, BPC and format selection, TMDS rate fallback, YUV420-only failures, DVI fallback, and connector disable. Reset-suite cases validate initial HDMI state values before atomic check fills computed fields. Mode-valid tests exercise default acceptance, hook-based rejection, total rejection, and EDID max-TMDS filtering. InfoFrame tests commit modesets with accept/reject HDMI callbacks and check whether failure counts change.

## State And Persistence
State is all in-memory KUnit/DRM state: connector EDID bytes, parsed `display_info`, mode lists, connector atomic HDMI fields (`broadcast_rgb`, `output_bpc`, `output_format`, `tmds_char_rate`, `is_limited_range`, InfoFrame state), CRTC `mode_changed`, and the fixture failure counter. No persistent storage is used. KUnit actions clean up DRM devices, atomic states, and display modes.

## Dependencies And Integration Points
This file integrates DRM atomic helpers, EDID parsing, HDMI state helpers, HDMI InfoFrame helpers, connector properties, mode validation, and the shared `drm_kunit_helpers` fixture layer. Test inputs come from `drm_kunit_edid.h`. It is sensitive to DRM mode constants, CEA VIC matching, HDMI Forum/CTA EDID interpretation, and `drmm_connector_hdmi_init()` property setup.

## Risks And Maintenance Notes
The largest risk is semantic drift in HDMI helper policy: output-format preference, RGB quantization rules, deep-color fallback order, max-TMDS filtering, or HDR property gating changes will require expected values to be updated. Many tests manually mutate atomic state and connector callback pointers, so they intentionally bypass normal driver layering. The `-EDEADLK` retry loops are necessary but verbose; missing a clear/backoff path could create flakes. EDID fixture changes can alter preferred mode ordering, `is_hdmi`, max TMDS, HDR property exposure, and 4:2:0-only decisions.

## Test Signals
Passing signals include expected BPC/format/TMDS rates, correct limited/full RGB decisions for auto/full/limited modes, `mode_changed` only when HDMI state changes require it, rejected modes disappearing from `connector->modes`, failed YUV420-only commits when the driver lacks YUV420, reset defaults of zero computed HDMI fields, and InfoFrame update failure counters changing only for programmed failing frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_hdmi_state_helper_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_kunit_edid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_kunit_edid.h

## Purpose
Static EDID fixture header for DRM HDMI KUnit tests. It provides raw base and CTA extension blocks that model DVI, HDMI 1080p, HDR, YUV/deep-color, constrained TMDS, and 4K YUV420-only/also-capable displays.

## Important APIs, Types, And Functions
The file exports no functions; it declares `static const unsigned char` arrays named `test_edid_dvi_1080p`, `test_edid_hdmi_1080p_rgb_max_100mhz`, `test_edid_hdmi_1080p_rgb_max_200mhz`, `test_edid_hdmi_1080p_rgb_max_200mhz_hdr`, `test_edid_hdmi_1080p_rgb_max_340mhz`, `test_edid_hdmi_1080p_rgb_yuv_dc_max_200mhz`, `test_edid_hdmi_1080p_rgb_yuv_dc_max_340mhz`, `test_edid_hdmi_1080p_rgb_yuv_4k_yuv420_dc_max_200mhz`, and `test_edid_hdmi_4k_rgb_yuv420_dc_max_340mhz`. Each array is accompanied by an `edid-decode` transcript documenting the intended capabilities and conformance.

## Control Flow
There is no runtime control flow in this header. Consumers pass the raw byte arrays and `ARRAY_SIZE()` into DRM EDID allocation/parsing helpers. The fixtures are selected by tests to force HDMI helper branches such as DVI behavior, max-TMDS rejection, RGB-only display constraints, YUV422/YUV444 support, YUV420-only 4K modes, HDR static metadata, and HDMI Forum deep-color data.

## State And Persistence
The EDID arrays are immutable test data compiled into the KUnit object. Their contents become transient parsed connector state only when a test calls `drm_edid_alloc()` and updates a connector.

## Dependencies And Integration Points
The header is tightly coupled to DRM EDID/CTA parsing and `drm_hdmi_state_helper_test.c`. The decoded comments document external expectations from `edid-decode`, including checksums, VICs, max TMDS clocks, colorimetry, deep-color flags, SCDC presence, and HDR metadata.

## Risks And Maintenance Notes
The arrays are binary fixtures, so small byte edits can silently change many parsed properties. The 100 MHz fixture is intentionally nonconformant to exercise filtering; it should not be generalized as a valid monitor. If EDID parser behavior changes, tests may fail because preferred modes, 4:2:0 capability maps, HDR property exposure, or `is_hdmi` classification change. Regenerate comments with a matching `edid-decode` version when fixture bytes are modified.

## Test Signals
Signals are indirect: consumers expect exact parsed display capabilities, mode availability, and conformance/failure semantics. Important observable values include 1080p/4K preferred modes, 640x480 fallback modes after filtering, max TMDS clocks of 100/200/340 MHz, HDR metadata availability, and YUV420-only versus YUV420-also mode classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_kunit_edid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_kunit_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_kunit_helpers.c

## Purpose
Shared helper library for DRM KUnit tests. It creates mock devices, DRM devices, atomic states, primary planes, CRTCs, connector enable commits, and auto-destroyed display modes so individual DRM tests can exercise real DRM helper code without a hardware driver.

## Important APIs, Types, And Functions
`drm_kunit_helper_alloc_device()` and `drm_kunit_helper_free_device()` wrap KUnit mock device registration. `__drm_kunit_helper_alloc_drm_device_with_driver()` allocates a DRM device with a supplied driver and initializes mode config with atomic helper config funcs. `drm_kunit_helper_atomic_state_alloc()` allocates a `drm_atomic_state`, attaches the acquire context, and registers a KUnit cleanup action. `drm_kunit_helper_create_primary_plane()` and `drm_kunit_helper_create_crtc()` build managed mock plane/CRTC objects with default atomic funcs when callbacks are omitted. `drm_kunit_helper_enable_crtc_connector()` performs a real atomic commit enabling a CRTC/connector route. `drm_kunit_add_mode_destroy_action()` and `drm_kunit_display_mode_from_cea_vic()` manage display-mode lifetimes.

## Control Flow
Device allocation flows through KUnit device resources and `__devm_drm_dev_alloc()`, followed by `drmm_mode_config_init()`. Plane/CRTC creation chooses default formats/modifiers/callbacks when callers pass `NULL`, then uses DRM managed allocation/initialization and helper attachment. Connector enablement allocates atomic state, gets connector and CRTC states, sets CRTC routing and mode, marks the CRTC enabled/active, and commits.

## State And Persistence
All state is test-scoped and managed by KUnit or DRMM actions. Atomic states are reference-counted and released by cleanup callbacks. Display modes created for tests are destroyed by KUnit actions. No persistent storage is used.

## Dependencies And Integration Points
The file exports GPL symbols consumed by many DRM KUnit suites. It depends on DRM atomic, managed device allocation, EDID/mode helpers, KUnit resources, KUnit mock devices, and platform-device support. Its default mode-config funcs wire mock devices into standard `drm_atomic_helper_check()` and `drm_atomic_helper_commit()`.

## Risks And Maintenance Notes
Mock defaults must stay compatible with DRM helper assumptions. A notable maintenance hazard is `drm_kunit_helper_create_primary_plane()` passing `default_plane_modifiers` to `__drmm_universal_plane_alloc()` even when a custom `modifiers` argument is supplied, which means custom modifiers would be ignored unless fixed. Assertions inside helper constructors abort tests on allocation/init failures, so helper changes can affect many suites at once.

## Test Signals
Signals are mostly downstream: tests should be able to allocate devices, create planes/CRTCs, enable connector routes, and clean resources without leaks or stale refs. Direct failure signals are KUnit assertions on allocation/init, atomic commit return codes, and mode-destroy action registration results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_kunit_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_managed_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_managed_test.c

## Purpose
KUnit tests for DRM managed action lifetime behavior. The suite verifies both explicit `drmm_release_action()` execution and automatic action execution when a DRM device is unregistered and its parent mock device is freed.

## Important APIs, Types, And Functions
`struct managed_test_priv` stores the mock `drm_device`, an `action_done` flag, and a waitqueue. `drm_action()` is the managed callback that sets the flag and wakes waiters. `drm_test_managed_release_action()` registers, explicitly releases, waits, and unregisters. `drm_test_managed_run_action()` registers and relies on device teardown to run the action. `drm_managed_test_init()` allocates the KUnit mock device and DRM device through `drm_kunit_helpers`.

## Control Flow
Each test registers `drm_action` with `drmm_add_action_or_reset()`, registers the DRM device, then triggers the action either explicitly or by `drm_dev_unregister()` plus `drm_kunit_helper_free_device()`. A waitqueue timeout of 100 ms bounds the assertion that the action was observed.

## State And Persistence
State is transient in `managed_test_priv`. The comment notes that the DRM device cannot be embedded in `priv` because the action flag must outlive the DRM/device release sequence. No persistent storage exists.

## Dependencies And Integration Points
The suite integrates DRM managed resource APIs, DRM device registration, the KUnit helper mock device, Linux waitqueues, and KUnit resource allocation. It exercises the action path used by DRM drivers to bind cleanup to `drm_device` lifetime.

## Risks And Maintenance Notes
The 100 ms timeout is intentionally small and can be fragile on very slow KUnit environments. Incorrect lifetime changes in DRM managed cleanup could either skip the action or free backing memory before the wait observes completion. Manual mock-device freeing inside tests must stay aligned with KUnit auto-cleanup semantics to avoid double cleanup.

## Test Signals
Passing signals are zero return from `drmm_add_action_or_reset()` and `drm_dev_register()`, positive waitqueue timeout return after action execution, and no teardown crash. Failing signals include timed-out wait, registration errors, or cleanup lifetime assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_managed_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_mm_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_mm_test.c

## Purpose
KUnit coverage for the DRM range allocator `drm_mm`. It checks initialization, hole tracking, node reservation/removal, debug printing, power-of-two alignment across 32-bit and 64-bit address spaces, and low/high insertion behavior.

## Important APIs, Types, And Functions
`insert_modes[]` maps readable names to `DRM_MM_INSERT_*` modes. `assert_no_holes()`, `assert_one_hole()`, `misalignment()`, and `assert_node()` validate allocator invariants. `drm_test_mm_init()` covers empty/full/empty transitions. `drm_test_mm_debug()` exercises `drm_mm_print()`. `expect_insert()` wraps `drm_mm_insert_node_generic()`. `drm_test_mm_align_pot()` allocates many aligned nodes over a near-full `u64` range. `drm_test_mm_once()` validates insertion into holes bounded by reserved low/high nodes.

## Control Flow
Tests initialize a `drm_mm`, reserve or insert nodes, inspect hole iterators and node fields, then remove nodes and call `drm_mm_takedown()`. The alignment tests iterate descending powers of two, allocate nodes with `kzalloc_obj()`, insert them with best-fit mode, periodically `cond_resched()`, and remove/free all nodes in a safe iterator. Low/high tests reserve nodes at positions 1 and 5 in a 7-unit space and insert a size-2 node into remaining holes using the requested mode.

## State And Persistence
Allocator state lives on the stack in `struct drm_mm` and `struct drm_mm_node` objects, with dynamic node allocations only in alignment tests. No persistent state exists. Cleanup removes allocated nodes and tears down the allocator.

## Dependencies And Integration Points
The file directly exercises `drm_mm.h` APIs and DRM debug printers. It depends on KUnit, kernel allocation helpers, `div64_u64_rem()`, `BIT_ULL()`, and scheduler rescheduling for large alignment loops.

## Risks And Maintenance Notes
Alignment tests cover large address ranges and may be slower than typical unit tests, though they bound allocation to one node per bit. Assertions assume current hole iterator semantics and insertion mode behavior; changes in best-fit/low/high policy can alter expected placement. `drm_test_mm_debug()` is a smoke test and does not validate exact output.

## Test Signals
Signals include correct initialized/clean state, one-hole and no-hole iterator counts, successful whole-range reservation/removal, no crash in debug printing, allocated nodes with expected size/alignment/color, and successful low/high insertion into valid holes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_mm_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_modes_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_modes_test.c

## Purpose
KUnit tests for DRM analog TV mode constructors. The suite verifies generated NTSC 480i, PAL 576i, and monochrome 576i timings and confirms inline convenience constructors match the generic `drm_analog_tv_mode()` output.

## Important APIs, Types, And Functions
`struct drm_test_modes_priv` holds a mock device and DRM device. `drm_test_modes_init()` builds them with `drm_kunit_helpers`. Test functions call `drm_analog_tv_mode()`, `drm_mode_analog_ntsc_480i()`, `drm_mode_analog_pal_576i()`, `drm_mode_vrefresh()`, and `drm_mode_equal()`. Created modes are registered with `drm_kunit_add_mode_destroy_action()`.

## Control Flow
Each test allocates one or two modes, registers destroy actions, then checks timing fields. NTSC asserts 60 Hz, 720 horizontal display, hsync start 736, htotal 858, vdisplay 480, and vtotal 525. PAL and monochrome assert 50 Hz, hsync start 732, htotal 864, vdisplay 576, and vtotal 625. Inline tests compare full mode equality against generic construction.

## State And Persistence
State is limited to mock DRM device objects and allocated `drm_display_mode` instances that KUnit destroys at test end. No persistent state exists.

## Dependencies And Integration Points
The suite integrates DRM mode generation, KUnit helper devices, and `linux/units.h` for `HZ_PER_KHZ`. It protects analog-TV timing helpers used by probe helpers and connector TV mode enumeration.

## Risks And Maintenance Notes
Expected timings are tied to BT.601 and analog TV assumptions. If DRM changes interlace timing representation, vrefresh rounding, or helper defaults, tests may need updates. Since the suite checks raw timing fields, it can catch both intentional timing policy changes and accidental arithmetic regressions.

## Test Signals
Signals are exact mode fields, vrefresh values, non-null mode allocation, successful destroy action registration, and `drm_mode_equal()` for generic versus convenience constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_modes_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_panic_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_panic_test.c

## Purpose
KUnit tests for DRM panic screen drawing. The suite verifies panic screen renderers write or address pixels correctly for mapped framebuffers, page-list framebuffers, and callback-driven pixel plotting across several resolutions and formats.

## Important APIs, Types, And Functions
`struct drm_test_mode` describes width, height, DRM fourcc format, draw function, and screen name. `DRM_TEST_MODE_LIST()` expands cases for user, kmsg, and optionally QR-code screens. `drm_test_panic_init()` allocates a `drm_scanout_buffer` and sets a panic description. `drm_test_panic_screen_user_map()` tests contiguous memory through `iosys_map`. `drm_test_panic_screen_user_page()` tests page-backed scanout buffers. `drm_test_panic_screen_user_set_pixel()` installs `drm_test_panic_set_pixel()` to assert bounds.

## Control Flow
For mapped buffers, the test fills vmalloc memory with `0xa5`, sets scanout dimensions/pitch/format, invokes the selected draw function, and checks bytes if panic colors are the configured defaults. For page buffers, it allocates pages, maps and pre-fills each page, draws, validates only bytes within framebuffer size, then frees pages. The set-pixel path never stores pixels; it asserts every callback coordinate is within bounds.

## State And Persistence
State is transient framebuffer memory or allocated pages plus one KUnit-owned `drm_scanout_buffer`. The global panic description is set for the test run. No persistent storage exists.

## Dependencies And Integration Points
The file integrates `drm_panic.h` draw functions, `drm_format_info()`, vmalloc, page allocation, `kmap_local_page()`, and optional `CONFIG_DRM_PANIC_SCREEN_QR_CODE`. Color-byte validation depends on `CONFIG_DRM_PANIC_BACKGROUND_COLOR` and `CONFIG_DRM_PANIC_FOREGROUND_COLOR`.

## Risks And Maintenance Notes
The byte validation is intentionally disabled for non-default panic colors, reducing coverage for custom configurations. Page allocation loops must clean up partially allocated pages correctly. Drawing algorithms that leave padding or untouched pixels could fail map/page tests. Large 1920x1080 allocations may be heavier than most KUnit cases.

## Test Signals
Signals include no allocation failures, all mapped/page framebuffer bytes rewritten to expected default color bytes, no out-of-bounds set-pixel callbacks, and parameter descriptions naming screen, resolution, and format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_panic_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_plane_helper_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_plane_helper_test.c

## Purpose
Parameterized KUnit tests for `drm_atomic_helper_check_plane_state()`. The file validates clipping, positioning, rotation/reflection-aware source adjustment, scaling limits, and invalid plane-state rejection.

## Important APIs, Types, And Functions
The static `crtc_state` models an active 1024x768 CRTC. `struct drm_check_plane_state_test` describes input source/destination rectangles, expected clipped rectangles, rotation, scale bounds, and positioning permission. `drm_plane_helper_init()` creates mock plane/framebuffer/plane-state objects for each parameter. `check_src_eq()` and `check_crtc_eq()` compare helper-produced fixed-point source and integer destination rectangles.

## Control Flow
Valid test cases call `drm_atomic_helper_check_plane_state()` and expect zero, visible state, and exact source/destination rectangles. Cases cover simple clipping, 90-degree rotation with reflection, allowed positioning, exact 2x upscaling/downscaling, and fixed-point rounding boundaries. Invalid cases expect negative return for prohibited positioning or scale factors outside configured min/max.

## State And Persistence
State is one KUnit-allocated mock plane, framebuffer, and plane state per parameter. The framebuffer is 2048x2048. No persistent state is used.

## Dependencies And Integration Points
The suite directly exercises DRM atomic plane helper clipping/scaling logic and uses DRM rect helpers and rotation flags. It protects behavior used by many atomic KMS drivers before programming hardware plane state.

## Risks And Maintenance Notes
Expected fixed-point values are sensitive to clipping and rounding policy. Changing helper rounding, visible-state rules, or rotation handling will produce exact-value failures. The mock CRTC uses `ZERO_SIZE_PTR` for pointers because only geometry is relevant; helper changes that dereference more CRTC fields could require a richer fixture.

## Test Signals
Signals are helper return values, `plane_state->visible`, exact fixed-point source rectangle, exact destination rectangle, non-negative source coordinates, and negative errors for invalid positioning/upscale/downscale cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_plane_helper_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_probe_helper_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_probe_helper_test.c

## Purpose
KUnit tests for `drm_connector_helper_tv_get_modes()`. The suite verifies analog TV mode enumeration, preferred-mode ordering, and command-line TV mode override behavior for connectors with NTSC and/or PAL support.

## Important APIs, Types, And Functions
`struct drm_probe_helper_test_priv` holds a mock DRM device, mock device, and connector. `drm_probe_helper_test_init()` initializes an atomic-capable DRM device and a managed connector with atomic state funcs. `struct drm_connector_helper_tv_get_modes_test` defines supported TV modes, default mode, optional cmdline override, and expected mode constructors. Macros `TV_MODE_TEST` and `TV_MODE_TEST_CMDLINE` build parameter rows.

## Control Flow
For each parameter, the test optionally marks a command-line TV mode, creates TV mode properties with `drm_mode_create_tv_properties()`, attaches the default property to the connector, locks the mode-config mutex, calls `drm_connector_helper_tv_get_modes()`, counts probed modes, and compares the first two modes against expected constructors. The first expected mode must be preferred; the second, if any, must not.

## State And Persistence
State resides in connector properties, `connector->cmdline_mode`, and `connector->probed_modes`. Expected modes allocated for comparison are destroyed by KUnit actions. No persistent storage exists.

## Dependencies And Integration Points
The test integrates DRM connector state helpers, mode config TV properties, analog TV mode constructors from `drm_modes`, and probe helper mode-list behavior. It complements `drm_modes_test.c` by validating connector-level ordering and preferred flags rather than raw timings.

## Risks And Maintenance Notes
Mode ordering is policy-sensitive: default and command-line overrides intentionally affect the first/preferred mode. Property or cmdline semantics changes can break expectations even if timing generation remains correct. The test currently checks up to two modes because supported cases are NTSC/PAL only.

## Test Signals
Signals include returned mode count, probed mode list length, exact mode equality for preferred and secondary modes, preferred flag only on the first mode, and zero modes when no supported TV modes are configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_probe_helper_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_rect_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_rect_test.c

## Purpose
KUnit coverage for DRM rectangle helpers. It validates scaled clipping, intersection, horizontal/vertical scale calculation, and rotation/inverse-rotation behavior including boundary cases with zero, negative, fixed-point, and non-overlapping rectangles.

## Important APIs, Types, And Functions
`drm_rect_compare()` checks coordinates and dimensions. Direct tests cover `drm_rect_clip_scaled()` for divide-by-zero prevention, unclipped cases, clipped cases, and signed-versus-unsigned regression behavior. Parameter tables drive `drm_rect_intersect()`, `drm_rect_calc_hscale()`, `drm_rect_calc_vscale()`, `drm_rect_rotate()`, and `drm_rect_rotate_inv()`.

## Control Flow
The scaled clipping tests initialize source/destination/clip rectangles, call `drm_rect_clip_scaled()`, and assert visibility plus exact source/destination results. Intersect parameters copy the first rect, intersect with the second, then compare visibility and mutated result. Scale parameters compute horizontal and vertical scale factors with min/max bounds. Rotation parameters rotate a rectangle in a given width/height space, then separately inverse-rotate the expected rectangle back to the original.

## State And Persistence
State is stack-local rectangle data and static parameter tables. No persistent state or allocated resources exist.

## Dependencies And Integration Points
The suite depends on `drm_rect.h`, DRM rotation flags from `drm_mode.h`, Linux errno values, and KUnit parameterization. It protects geometry helpers used by plane clipping, scaling validation, and framebuffer coordinate transformations across DRM drivers.

## Risks And Maintenance Notes
Expected values encode exact current geometry semantics, including non-visible rectangles that may retain negative widths/heights after intersection. Fixed-point clipping and scale results are particularly sensitive to rounding behavior. The signed-versus-unsigned regression guards against a historical class of negative-width visibility bugs.

## Test Signals
Signals include false visibility for zero/non-overlapping scaled rectangles, exact clipped source/destination rectangles, correct intersection geometry for overlap/touch/far-away cases, `-ERANGE` and `-EINVAL` scale failures, and round-trip equivalence of rotate plus inverse rotate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_rect_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_sysfb_modeset_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_sysfb_modeset_test.c

## Purpose
KUnit tests for `drm_sysfb_build_fourcc_list()`, the helper that derives a DRM format list for system framebuffers while ensuring XRGB8888 fallback support, de-duplicating formats, and replacing alpha variants with equivalent opaque formats.

## Important APIs, Types, And Functions
`struct sysfb_build_fourcc_list_case` describes native fourcc inputs and expected output. Parameter cases cover no native formats, native XRGB8888, duplicate removal, alpha-to-X format conversion, and mixed random formats. `drm_test_sysfb_build_fourcc_list()` allocates a mock DRM device and calls `drm_sysfb_build_fourcc_list()`.

## Control Flow
For each case, the test builds a mock device through `drm_kunit_helpers`, calls the sysfb helper with a fixed output buffer size of 50, then checks returned count and full output buffer memory against the expected array. The expected arrays preserve input order after normalization while ensuring an opaque XRGB8888 fallback appears where needed.

## State And Persistence
State is static parameter data, a stack output array, and transient mock device/DRM device resources. No persistent state exists.

## Dependencies And Integration Points
The test includes `../sysfb/drm_sysfb_helper.h` and uses DRM fourcc definitions plus shared KUnit helpers. It protects sysfb integration used when firmware/system framebuffers are handed to DRM modeset clients.

## Risks And Maintenance Notes
The `remove duplicates` case sets `native_fourccs_size = 11` despite initializing more values, so only the first 11 entries are intentionally passed. Full-buffer `KUNIT_EXPECT_MEMEQ()` means unused output slots are expected to remain zero. Any helper policy change around fallback ordering, duplicate retention, or alpha conversion will require expected arrays to change.

## Test Signals
Signals include exact number of output formats, exact normalized fourcc order, no duplicate retained formats, alpha formats converted to corresponding X formats, and XRGB8888 present for fallback when needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_sysfb_modeset_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/Kconfig

## Purpose
Kconfig entry for the TI Keystone Display SubSystem DRM driver. It exposes `CONFIG_DRM_TIDSS` as a tristate option for Keystone-family SoCs and compile-test builds.

## Important APIs, Types, And Functions
The file defines `config DRM_TIDSS` with prompt `DRM Support for TI Keystone`. It depends on `DRM && OF`, and on `ARM || ARM64 || COMPILE_TEST`. It selects `DRM_CLIENT_SELECTION`, `DRM_KMS_HELPER`, `DRM_DISPLAY_HELPER`, `DRM_BRIDGE_CONNECTOR`, and `DRM_GEM_DMA_HELPER`.

## Control Flow
There is no runtime control flow. During kernel configuration, enabling this option allows the Makefile to build `tidss.o` as built-in or module depending on the selected tristate value.

## State And Persistence
The persistent state is the generated kernel configuration value for `CONFIG_DRM_TIDSS`. That value controls compilation and module availability.

## Dependencies And Integration Points
The option integrates the TIDSS driver with the DRM core, Open Firmware/device-tree based platform discovery, KMS helpers, display helpers, bridge connector support, and DMA GEM helpers. The help text documents target SoCs: 66AK2Gx, AM65x, and J721E.

## Risks And Maintenance Notes
Incorrect dependencies could expose the driver on unsupported architectures or hide compile-test coverage. Missing selected helper libraries would surface as link errors. The prompt says Keystone while the supported family list spans multiple TI DSS variants; update help text if supported SoCs change.

## Test Signals
Signals are build-time: `CONFIG_DRM_TIDSS=y/m` should compile and link the objects from the tidss Makefile on supported or compile-test configurations, and be unavailable when core DRM/OF dependencies are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/Makefile

## Purpose
Build recipe for the TI Keystone/TIDSS DRM driver object. It lists all component objects that are linked into `tidss.o` and binds that aggregate to `CONFIG_DRM_TIDSS`.

## Important APIs, Types, And Functions
`tidss-y` includes `tidss_crtc.o`, `tidss_drv.o`, `tidss_encoder.o`, `tidss_kms.o`, `tidss_irq.o`, `tidss_plane.o`, `tidss_scale_coefs.o`, `tidss_dispc.o`, and `tidss_oldi.o`. `obj-$(CONFIG_DRM_TIDSS) += tidss.o` connects the aggregate object to the Kconfig option.

## Control Flow
There is no runtime flow. Kbuild collects listed objects into `tidss.o`; when `CONFIG_DRM_TIDSS` is `m`, the result becomes a module, and when `y`, it is built into the kernel.

## State And Persistence
Persistent build state is determined by Kbuild outputs and the kernel configuration. The Makefile itself stores the authoritative object composition for the driver.

## Dependencies And Integration Points
The object list reflects driver layering: CRTC, plane, encoder, KMS/device glue, IRQ handling, scaling coefficients, DISPC hardware access, and OLDI output support. It integrates with the parent DRM Kbuild tree through `obj-*`.

## Risks And Maintenance Notes
Adding or removing source files without updating `tidss-y` can produce missing symbols or dead code. Object order is usually not semantically important but can affect initcall/link diagnostics. New optional features may need conditional object inclusion rather than unconditional `tidss-y`.

## Test Signals
Signals are compile/link success for built-in and module builds, presence of all expected symbols in `tidss.o`, and no stale object references after source file renames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_crtc.c

## Purpose
CRTC implementation for the TI Display SubSystem DRM driver. It maps DRM atomic CRTC operations, vblank handling, page-flip event completion, mode validation, plane overlay positioning, runtime power, and color management onto TIDSS/DISPC videoport hardware.

## Important APIs, Types, And Functions
IRQ entry points are `tidss_crtc_vblank_irq()`, `tidss_crtc_framedone_irq()`, and `tidss_crtc_error_irq()`. Atomic helper callbacks include `tidss_crtc_atomic_check()`, `tidss_crtc_atomic_flush()`, `tidss_crtc_atomic_enable()`, `tidss_crtc_atomic_disable()`, and `tidss_crtc_mode_valid()`. `tidss_crtc_position_planes()` programs overlay layers based on normalized z-position and visibility. CRTC funcs cover vblank enable/disable, state reset/duplicate/destroy, and object destruction. `tidss_crtc_create()` allocates and initializes the CRTC.

## Control Flow
Atomic check rejects invalid enabled modes with `dispc_vp_mode_valid()`, updates CRTC info for modesets, then delegates bus validation to `dispc_vp_bus_check()`. Flush for non-modeset commits verifies GO is idle, sets videoport properties and plane positions, obtains a vblank ref, asserts GO, stores the pending event under `event_lock`, and lets the vblank IRQ complete it. Enable gets runtime PM, sets and enables the videoport clock, configures the videoport and planes, turns vblank on, prepares/enables hardware, and sends any enable event immediately. Disable reinitializes framedone completion, disables all overlay layers as a hardware workaround, disables the videoport, waits up to 500 ms for framedone, unprepares, sends pending event, turns vblank off, disables clock, and drops runtime PM.

## State And Persistence
Persistent runtime state is in `struct tidss_crtc`: embedded DRM CRTC, hardware videoport id, pending vblank event, and framedone completion. Extended atomic state stores `plane_pos_changed`, `bus_format`, and `bus_flags`. Hardware state lives in DISPC videoport clocks, GO bit, overlay layer enable/position, and vblank/framedone IRQ state. No filesystem persistence exists.

## Dependencies And Integration Points
The file integrates DRM atomic helpers, vblank/event locking, TIDSS runtime PM, IRQ control, `tidss_plane` zpos/hardware ids, DISPC videoport and overlay APIs, and DRM color management. It is linked into the TIDSS driver by the Makefile and exposed through prototypes in `tidss_crtc.h`.

## Risks And Maintenance Notes
Event lifetime is delicate: `drm_crtc_vblank_get()` must pair with vblank completion, and pending events are protected by `event_lock`. The GO-bit race before vblank is explicitly handled in `tidss_crtc_finish_page_flip()`. Early returns after runtime get or clock setup failures in enable do not visibly unwind prior steps in this function, so callers rely on surrounding atomic error handling. Plane-position programming assumes all affected planes are present in atomic state. Disable depends on framedone IRQ delivery and logs a timeout after 500 ms.

## Test Signals
Signals are primarily integration/runtime: successful atomic modesets, valid mode rejection through `MODE_*`, vblank events delivered once, page flips completed after GO clears, no sync-lost errors under plane reuse, framedone completion during disable, and color-management properties exposed with expected gamma/CTM support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_crtc.h

## Purpose
Public CRTC declarations for the TIDSS DRM driver. The header defines the driver-specific CRTC container, extended CRTC atomic state, conversion macros, IRQ hooks, and CRTC creation entry point.

## Important APIs, Types, And Functions
`struct tidss_crtc` embeds `struct drm_crtc`, stores `hw_videoport`, a pending `drm_pending_vblank_event *event`, and `struct completion framedone_completion`. `to_tidss_crtc()` converts a DRM CRTC pointer to the driver container. `struct tidss_crtc_state` embeds `struct drm_crtc_state` first and adds `plane_pos_changed`, `bus_format`, and `bus_flags`; `to_tidss_crtc_state()` converts base state pointers. Exported functions are `tidss_crtc_vblank_irq()`, `tidss_crtc_framedone_irq()`, `tidss_crtc_error_irq()`, and `tidss_crtc_create()`.

## Control Flow
The header itself has no executable flow. It defines the type contracts used by CRTC implementation, IRQ dispatch, KMS initialization, and other TIDSS modules that need to create CRTCs or notify them of videoport interrupts.

## State And Persistence
State fields declared here persist for the lifetime of the CRTC object and individual atomic CRTC states. The pending event and completion coordinate asynchronous IRQ-driven state transitions. No external persistence exists.

## Dependencies And Integration Points
The header depends on Linux completion/wait declarations and DRM CRTC types. It forward-declares `struct tidss_device` to avoid pulling in full driver headers. It is included by `tidss_crtc.c` and likely by IRQ/KMS setup code.

## Risks And Maintenance Notes
`struct tidss_crtc_state` requires `base` to remain first because helper conversion assumes container layout. Any new fields added to the state must be copied/reset in duplicate/reset paths in `tidss_crtc.c`. Event and completion fields are concurrency-sensitive and must be accessed with the locking/waiting rules implemented by the C file.

## Test Signals
Signals are compile-time and integration-time: correct container conversions, successful CRTC creation, IRQ code linking to declared hooks, and extended state fields preserved across duplicate/reset/destroy operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_crtc.h -->
