# subset-b-003753

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_connector_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_connector_test.c

Purpose: provides KUnit coverage for DRM connector construction, dynamic connector registration, HDMI connector metadata validation, connector helper string lookups, broadcast RGB property attachment, and HDMI TMDS clock calculation. Although the file comment mentions modes, the test body is centered on connector lifecycle and HDMI-specific connector helper behavior.

Important APIs/types/functions: `struct drm_connector_init_priv` owns the mock `drm_device`, `drm_connector`, and dummy I2C DDC adapter shared by most suites. `drm_test_connector_init()` allocates the test device through DRM KUnit helpers, initializes a dummy `i2c_adapter`, registers cleanup with `kunit_add_action_or_reset()`, and stores the fixture in `test->priv`. The file exercises `drmm_connector_init()`, `drm_connector_dynamic_init()`, `drm_connector_dynamic_register()`, `drmm_connector_hdmi_init()`, `drm_get_tv_mode_from_name()`, `drm_hdmi_connector_get_broadcast_rgb_name()`, `drm_hdmi_connector_get_output_format_name()`, `drm_connector_attach_broadcast_rgb_property()`, and `drm_hdmi_compute_mode_clock()`. Dummy `drm_connector_funcs`, `drm_connector_hdmi_funcs`, and `i2c_algorithm` instances isolate the tests from real hardware.

Control flow: the suite is split into multiple `kunit_suite` blocks. Plain `drmm_connector_init` tests validate that normal and NULL-DDC connectors initialize and that all defined connector types pass. Dynamic-init tests verify successful initialization, no list insertion before registration, default property attachment, connector type coverage, and generated names. Dynamic-register tests are separated into "early" registration before `drm_dev_register()` and registration after device registration; the early path expects deferred userspace registration and no mode object lookup, while the post-register path expects mode object insertion, sysfs device creation, sysfs name shape, and debugfs entry creation when `CONFIG_DEBUG_FS` is enabled. HDMI initialization tests validate vendor/product NULL and length handling, valid type restrictions to HDMI-A/HDMI-B, maximum bpc handling, HDR metadata property attachment for bpc greater than 8, supported-format requirements, and the relationship between YUV420 support and `connector.ycbcr_420_allowed`. Later suites are pure helper checks for TV mode parsing, HDMI enum-name helpers, broadcast RGB property attachment, and TMDS rate calculations for RGB, YUV420, YUV422, double-clock VICs, and invalid deep-color VIC 1 cases.

State and persistence: state is entirely in-memory KUnit fixture state plus transient DRM core objects. Tests mutate `connector->state`, `connector->base` properties, connector list links, registration state, mode object IDs, sysfs/debugfs pointers, HDMI vendor/product arrays, HDMI supported formats, and max-bpc/HDR property state. The dummy I2C adapter is registered with the kernel I2C core and removed through a KUnit action. `drm_dev_register()`/`drm_dev_unregister()` are used in the dynamic-register suite, so some tests briefly create DRM minor/sysfs/debugfs state. There is no filesystem persistence.

Dependencies and integration points: depends on DRM KUnit device allocation helpers, DRM atomic connector state helpers, DRM connector/mode/property internals via `../drm_crtc_internal.h`, Linux I2C adapter registration, CEA VIC mode construction through `drm_kunit_display_mode_from_cea_vic()`, and HDMI helper definitions from `drm/display/drm_hdmi_helper.h`. It is an integration-style KUnit test for DRM core connector internals rather than a mock-only unit test.

Risks: the dynamic registration tests touch global DRM registration paths, sysfs/debugfs behavior, and mode-object lookup, so environment configuration can affect assertions, especially debugfs. HDMI validation expectations are tightly coupled to the accepted bpc set, maximum vendor/product lengths, and color-format policy; changes in HDMI policy require corresponding test updates. The fixture reuses a single embedded connector per test case and relies on KUnit suite exit cleanup to avoid list/refcount leakage. `drm_connector_dynamic_register_mode_object()` obtains a looked-up connector reference and compares it without an explicit `drm_connector_put()` in the shown code, so reference semantics around lookup are worth watching if tests are refactored.

Test signals: KUnit case pass/fail for connector init, registration, property presence/defaults, sysfs/debugfs registration, HDMI validation return codes, string helper outputs, and exact TMDS character rates. Good regression signals include failures on connector list insertion, incorrect `registration_state`, missing default connector properties, HDR metadata property attachment at wrong bpc, YUV420 gating mistakes, or clock-math changes for VIC 1 and YUV420 legal VICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_connector_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_damage_helper_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_damage_helper_test.c

Purpose: tests `drm_atomic_helper_damage_iter` and `drm_atomic_for_each_plane_damage()` behavior for full-plane fallback damage, explicit framebuffer damage clips, clipping against plane source rectangles, fractional 16.16 source coordinates, moved source rectangles, invisible planes, missing CRTCs, and missing framebuffers.

Important APIs/types/functions: `struct drm_damage_mock` embeds enough DRM state to run the damage helpers: driver/device, plane, property, framebuffer, current plane state, old plane state, and object property storage. `drm_damage_helper_init()` configures a 2048x2048 framebuffer, marks the current plane visible with a non-NULL dummy CRTC (`ZERO_SIZE_PTR`), wires old/current state to the plane, installs `prop_fb_damage_clips`, and calls `drm_plane_enable_fb_damage_clips()`. Local helpers `set_plane_src()`, `set_damage_clip()`, `set_damage_blob()`, `set_plane_damage()`, and `check_damage_clip()` keep the cases compact and enforce rounded source bounds.

Control flow: each test configures old and current plane source rectangles, optionally attaches a `drm_property_blob` containing one or more `drm_mode_rect` damage clips, initializes `drm_atomic_helper_damage_iter`, iterates with `drm_atomic_for_each_plane_damage`, counts hits, and checks returned `drm_rect` clips. No-damage tests expect a full rounded source rectangle when the plane is visible and unchanged enough to require fallback damage, but zero hits when the current plane is invisible, lacks a CRTC, or lacks a framebuffer. Single-damage tests check exact clip returns, intersection against source bounds, dropped clips outside the source, fractional-source rounding, and the rule that a moved source falls back to full source damage. Multi-damage tests validate ordered multiple clips, one-intersect/one-outside filtering, full-source fallback on source movement, and no damage for invisible planes even when clips are present.

State and persistence: all state is per-test memory allocated by KUnit. The tests mutate `drm_plane_state` fields including `src_x`, `src_y`, `src_w`, `src_h`, `src`, `visible`, `crtc`, `fb`, and `fb_damage_clips`. The property blob objects are stack-local and point to stack-local damage rectangles. There is no persistent global state or filesystem output.

Dependencies and integration points: depends on DRM damage helpers, plane/framebuffer state definitions, and the DRM property system enough for `drm_plane_enable_fb_damage_clips()` to attach a damage-clips property. It validates helper semantics that real atomic plane update paths use to decide which framebuffer regions need repainting or flushing.

Risks: source coordinates are 16.16 fixed point while damage clips are integer rectangles, making off-by-one rounding bugs likely at fractional boundaries. Moved source handling deliberately ignores explicit damage and returns full source damage; callers relying on damage minimization can regress if this contract changes. The mock uses `ZERO_SIZE_PTR` as a non-NULL CRTC sentinel and minimal property/device setup, so tests validate helper logic but not full atomic state integration. Blob length and clip storage are trusted in test setup; malformed user damage blobs are outside this file's coverage.

Test signals: KUnit failures identify exact expected hit counts and clip coordinates. Strong signals include wrong rounded full-source rectangles, leaked outside-source damage, missing fallback damage on source movement, failure to filter invisible/no-CRTC/no-FB planes, and incorrect ordering or filtering of multi-clip damage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_damage_helper_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_dp_mst_helper_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_dp_mst_helper_test.c

Purpose: validates DisplayPort MST helper math and sideband request serialization. It covers PBN calculation for modes, virtual-channel payload bandwidth divisor calculation across DP link rates/lane counts, and encode/decode round trips for MST sideband request bodies.

Important APIs/types/functions: table types `drm_dp_mst_calc_pbn_mode_test`, `drm_dp_mst_calc_pbn_div_test`, and `drm_dp_mst_sideband_msg_req_test` drive parameterized KUnit cases. The tests call `drm_dp_calc_pbn_mode()`, `drm_dp_get_vc_payload_bw()`, `drm_dp_encode_sideband_req()`, and `drm_dp_decode_sideband_req()`. `sideband_msg_req_equal()` performs custom comparisons for request bodies containing dynamically allocated byte arrays or transaction arrays, while default cases are compared with `memcmp()`. `drm_test_dp_mst_msg_printf()` adapts `drm_printer` output into KUnit diagnostics for failed round trips.

Control flow: PBN mode cases pass pixel clock and bpp shifted into DP's fixed-point bpp representation, then compare exact integer PBN values. PBN divisor cases use a local `fixed20_12` initializer to compare `.full` values for UHBR and DP1.4 style rates across 1/2/4 lanes. Sideband cases define one focused field per request variant: port-number requests, payload allocation/query fields, remote DPCD read/write fields, remote I2C read/write transactions, and stream encryption status fields. The sideband test allocates input/output request bodies and a tx message, encodes the input, decodes into output, compares semantic equality, dumps both request bodies on mismatch, and frees decoded dynamic buffers for request types that allocate them.

State and persistence: test state is stack-local or KUnit-managed heap memory. Decoded request payloads can allocate `bytes` arrays in DPCD/I2C cases; the test explicitly frees those allocations after comparison. No state is persisted beyond KUnit output.

Dependencies and integration points: includes public `drm/display/drm_dp_mst_helper.h` plus internal MST topology definitions from `../display/drm_dp_mst_topology_internal.h`, so it directly covers internal encoding/decoding contracts used by the MST topology manager. The math tests anchor DP bandwidth accounting used by MST payload allocation.

Risks: exact fixed-point expected values make the tests sensitive to rounding policy; changing specification interpretation or precision will require test updates. `sideband_msg_req_equal()` intentionally uses `memcmp()` for many union cases, which assumes padding and uninitialized fields are deterministic in the test fixtures. The sideband request table focuses on field coverage rather than full valid protocol messages, so it catches serializer field loss but not all protocol validity failures. Manual freeing in the decode test must stay synchronized with allocation behavior of `drm_dp_decode_sideband_req()`.

Test signals: KUnit parameter descriptions show clock/bpp/DSC, link/lane combinations, or request descriptions. Failures indicate PBN math drift, bandwidth divisor rounding changes, sideband field packing/unpacking errors, or decoded buffer ownership regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_dp_mst_helper_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_exec_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_exec_test.c

Purpose: provides KUnit coverage for the DRM exec helper's object locking, duplicate handling, prepare helpers, and loop lifecycle. The tests target the `drm_exec` API used by drivers to lock multiple GEM reservation objects under wound/wait retry rules.

Important APIs/types/functions: `struct drm_exec_priv` stores a parent device and DRM device allocated by `drm_exec_test_init()` using DRM KUnit helpers. Tests call `drm_exec_init()`, `drm_exec_fini()`, `drm_exec_until_all_locked`, `drm_exec_lock_obj()`, `drm_exec_unlock_obj()`, `drm_exec_retry_on_contention()`, `drm_exec_prepare_obj()`, and `drm_exec_prepare_array()`. GEM objects are initialized with `drm_gem_private_object_init()` and finalized where needed with `drm_gem_private_object_fini()`.

Control flow: `sanitycheck()` only initializes/finalizes an exec object. `test_lock()` creates one GEM object and locks it inside the `drm_exec_until_all_locked` retry loop. `test_lock_unlock()` locks, unlocks, and relocks the same object within one exec context. `test_duplicates()` initializes with `DRM_EXEC_IGNORE_DUPLICATES`, locks the same object twice, then explicitly unlocks once before finalization. `test_prepare()` uses `drm_exec_prepare_obj()` to prepare one object with a single fence slot. `test_prepare_array()` allocates two GEM objects and prepares them together. `test_multiple_loops()` verifies separate exec loop instances can be initialized and finalized back to back without stale state.

State and persistence: state is limited to KUnit allocations, transient `struct drm_exec`, embedded GEM object reservation state, and object reference/lock state. There is no persistent storage. Some tests use stack-allocated GEM objects, while the array test uses KUnit-allocated heap objects and explicit GEM finalization.

Dependencies and integration points: depends on DRM device/GEM core initialization through `DRIVER_MODESET`, Linux prime-number support indirectly through `drm_exec`, and the reservation locking machinery behind GEM objects. The tests are direct API users and serve as examples of the required retry-loop idiom.

Risks: the tests mostly cover uncontended paths; they do not simulate actual ww-mutex contention, interrupts, or deadlock retries. Stack-allocated GEM objects must be correctly initialized before locking and finalized when object lifetime requires it. `test_duplicates()` depends on duplicate-ignore semantics balancing lock/unlock accounting. Changes to `drm_exec_until_all_locked` macro behavior can affect control-flow assumptions, especially around `ret` assignment and retry labels.

Test signals: KUnit failures show nonzero returns from lock/prepare helpers or loop/finalization problems. Regression signals include duplicate locking returning an error under `DRM_EXEC_IGNORE_DUPLICATES`, prepare-array failure for multiple objects, or state leakage preventing consecutive exec loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_exec_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_fixp_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_fixp_test.c

Purpose: tests core fixed-point conversion helpers in `drm_fixed.h`, specifically integer-to-fixed, fraction-to-fixed, and signed-magnitude-to-fixed conversions used by DRM math code.

Important APIs/types/functions: the tests call `drm_int2fixp()`, `drm_fixp_from_fraction()`, and `drm_sm2fixp()`. They rely on `DRM_FIXED_POINT` defining the fractional-bit position and use exact 64-bit constants to validate sign and fraction placement.

Control flow: `drm_test_int2fixp()` checks exact encodings for 1, -1, cancellation of `1 + -1`, positive and negative halves, and simple addition/subtraction combinations involving fixed 0.5 and fixed integer 1. `drm_test_sm2fixp()` first confirms the signed 63-bit maximum literal, then checks signed-magnitude encodings for +1, -1, +0.5, and -0.5 by comparing them against the integer/fraction helper outputs.

State and persistence: no mutable state is kept. All checks are pure arithmetic KUnit expectations.

Dependencies and integration points: depends only on KUnit and `drm/drm_fixed.h`. The covered helpers underpin DRM calculations that need stable fixed-point encodings without floating point in kernel code.

Risks: exact bit-level expectations make the tests sensitive to any representation change. Coverage is intentionally narrow: it does not cover overflow, rounding beyond simple halves, large numerators/denominators, division-by-zero behavior, or multiplication/division helpers. Comments in two subtraction cases contain wording mistakes but the assertions are clear.

Test signals: failures indicate a fundamental fixed-point representation or sign-conversion regression. Because the expected values are exact, failures should be high confidence and easy to localize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_fixp_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_format_helper_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_format_helper_test.c

Purpose: validates DRM framebuffer format helper conversions and copy helpers. It exercises XRGB8888 conversion into many destination formats, byte swapping, BGR/XBGR/ABGR channel reordering, mono conversion, clip-offset calculation, and multi-plane `drm_fb_memcpy()` behavior.

Important APIs/types/functions: the central fixture is `struct convert_xrgb8888_case`, which defines source pitch, clip rectangle, source XRGB8888 pixels, and expected outputs for gray8, RGB332, RGB565, XRGB1555, ARGB1555, RGBA5551, RGB888, BGR888, ARGB8888, XRGB2101010, ARGB2101010, mono, byte-swapped XRGB8888, XBGR8888, and ABGR8888. Global `fmtcnv_state_mem` and `fmtcnv_state` provide a preallocated `drm_format_conv_state`. Utility helpers calculate destination buffer size, convert little-endian test buffers to CPU order, convert CPU arrays to little-endian source arrays, and describe parameters. The tests call `drm_fb_xrgb8888_to_gray8()`, `drm_fb_xrgb8888_to_rgb332()`, `drm_fb_xrgb8888_to_rgb565()`/`rgb565be()`, `drm_fb_xrgb8888_to_xrgb1555()`, `drm_fb_xrgb8888_to_argb1555()`, `drm_fb_xrgb8888_to_rgba5551()`, `drm_fb_xrgb8888_to_rgb888()`, `drm_fb_xrgb8888_to_bgr888()`, `drm_fb_xrgb8888_to_argb8888()`, `drm_fb_xrgb8888_to_xrgb2101010()`, `drm_fb_xrgb8888_to_argb2101010()`, `drm_fb_xrgb8888_to_mono()`, `drm_fb_swab()`, `drm_fb_xrgb8888_to_bgrx8888()`, `drm_fb_xrgb8888_to_xbgr8888()`, `drm_fb_xrgb8888_to_abgr8888()`, `drm_fb_clip_offset()`, and `drm_fb_memcpy()`.

Control flow: parameterized conversion tests allocate destination buffers sized from destination format, pitch, clip, and plane; wrap source/destination in `iosys_map`; convert source fixtures to little-endian; optionally pass NULL destination pitch to request default pitch; run the helper; endian-normalize output where necessary; and compare exact bytes/words/dwords. Many conversion tests then clear the destination and call the helper again, checking repeatability and state reuse. `drm_test_fb_swab()` also tests the alias helper and a mock big-endian format flag. `drm_test_fb_clip_offset()` verifies offsets for horizontal, vertical, and combined clip offsets with default and custom pitches. `drm_test_fb_memcpy()` iterates over planes for XRGB8888-like, XRGB8888_A8, and YUV444 formats, allocates per-plane buffers, runs `drm_fb_memcpy()`, checks exact plane contents, clears, and repeats.

State and persistence: state is KUnit-managed heap memory plus the file-scope preallocated format conversion buffer. Tests mutate local `drm_framebuffer` structures, `iosys_map` wrappers, temporary output buffers, and a mock copied `drm_format_info` with `DRM_FORMAT_BIG_ENDIAN` set. There is no persistent state, but the shared conversion state means helpers are implicitly tested for safe reuse across repeated calls.

Dependencies and integration points: depends on DRM format metadata, framebuffer structures, rectangle helpers, `iosys_map`, GEM framebuffer helper headers, and DRM internal CRTC declarations. It directly covers conversion helpers used by simple display pipelines, fbdev emulation, shadow-plane update paths, and drivers that need CPU-side format conversion or copies.

Risks: expected buffers are dense and hand-maintained, so fixture mistakes are possible and can be hard to audit. The use of little-endian conversion helpers makes host-endian behavior explicit, but platform differences remain an important reason for these tests. `conversion_buf_size()` returns `size_t` while using `-EINVAL` for invalid format, though tests only pass valid formats. The shared preallocated conversion state could hide allocation-path issues that occur when helpers allocate temporary state dynamically. Most conversion functions are tested from XRGB8888 only, not all possible source formats.

Test signals: KUnit failures include parameter names such as `single_pixel_source_buffer`, `single_pixel_clip_rectangle`, `well_known_colors`, and `destination_pitch`, making it clear whether the regression is pixel conversion, clipping, pitch padding, endian swapping, alpha/channel filling, mono packing, clip offset, or multi-plane copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_format_helper_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_format_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_format_test.c

Purpose: tests DRM fourcc format metadata helpers for block width, block height, and minimum pitch calculation across invalid input, one-plane packed formats, two-plane NV12, three-plane YUV422, and tiled/block formats.

Important APIs/types/functions: the tests use `drm_format_info()` to fetch `struct drm_format_info` entries and then call `drm_format_info_block_width()`, `drm_format_info_block_height()`, and `drm_format_info_min_pitch()`. Formats under test include `DRM_FORMAT_XRGB4444`, `DRM_FORMAT_NV12`, `DRM_FORMAT_YUV422`, `DRM_FORMAT_X0L0`, `DRM_FORMAT_RGB332`, `DRM_FORMAT_RGB888`, `DRM_FORMAT_ABGR8888`, and `DRM_FORMAT_X0L2`.

Control flow: invalid tests pass NULL format info and invalid plane indices, expecting zero. Block width/height tests verify per-plane values and zero for out-of-range negative or too-large plane indices. Pitch tests cover 8/16/24/32 bpp packed formats at widths 0, small widths, common display widths, odd widths, and near-`UINT_MAX` widths to force 64-bit scaling. Multi-plane tests verify chroma pitch behavior for NV12 and YUV422, including rounded chroma width cases. Tiled tests validate block-derived pitch for X0L2.

State and persistence: no mutable state is kept. All tests are pure metadata lookups and arithmetic expectations.

Dependencies and integration points: depends on DRM fourcc format tables and KUnit. These helpers feed framebuffer validation, CPU copy/conversion helpers, plane size checks, and driver pitch validation.

Risks: exact expected pitch arithmetic makes the tests sensitive to metadata table changes and block-size definitions. The tests intentionally expect 64-bit pitch results for `UINT_MAX`-scale widths, so regressions often indicate overflow truncation. Coverage uses representative formats, not every fourcc entry, so new or exotic formats may need additional cases.

Test signals: failures isolate to invalid handling, block width, block height, or min-pitch arithmetic. Important regression signals include returning nonzero for invalid planes, losing 64-bit pitch precision, or miscomputing chroma/tiled pitches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_format_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_framebuffer_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_framebuffer_test.c

Purpose: tests DRM framebuffer command validation and framebuffer object lifecycle helpers. It covers `drm_internal_framebuffer_create()` validation gates, modifier support policy, source-coordinate bounds checking, framebuffer list cleanup, ID lookup, initialization validation, device mismatch rejection, and final free behavior.

Important APIs/types/functions: `struct drm_framebuffer_test` pairs a `drm_mode_fb_cmd2` command with expected creation delegation. `drm_framebuffer_create_cases[]` is the main validation matrix for ABGR8888, NV12, YVU420, YUV420_10BIT, and X0L2 commands, including dimensions, handles, pitches, offsets, flags, and modifiers. `struct drm_framebuffer_test_priv` embeds a mock `drm_device` and booleans for whether create/free callbacks fired. `fb_create_mock()` records when validation reached the driver `fb_create` callback and then returns `-EINVAL`, letting tests distinguish DRM core validation from driver allocation. Other tests call `drm_framebuffer_check_src_coords()`, `drm_framebuffer_init()`, `drm_framebuffer_cleanup()`, `drm_framebuffer_lookup()`, `drm_framebuffer_put()`, `drm_framebuffer_free()`, and `drm_mode_object_find()`.

Control flow: `drm_framebuffer_test_init()` allocates a DRM test device, sets min/max width/height, and installs mock mode-config funcs. The parameterized create test clears `buffer_created`, calls `drm_internal_framebuffer_create()`, and checks whether the mock callback was reached for each command. The matrix includes valid minimum/maximum sizes, too-small pitches, invalid dimensions, missing handles/formats, invalid flags, large offsets, unused-plane fields, modifier flag interactions, per-plane modifier consistency, and inexistent-plane fields. Modifier-not-supported testing sets `fb_modifiers_not_supported` and expects rejection before callback. Source-coordinate tests check overflow/ENOSPC with 16.16 source sizes. Lifecycle tests initialize one or more framebuffers, check list/refcount/mode-object fields, look up by ID, handle missing IDs, reject bad format or wrong device, cleanup list counts, and ensure `drm_framebuffer_free()` removes mode objects and calls `funcs->destroy()`.

State and persistence: state is held in the mock DRM device's `mode_config`, framebuffer list, mode-object IDR, and framebuffer object refcounts. Tests mutate `num_fb`, `fb_list`, `base.id`, `base.refcount`, `comm`, and callback flags. All state is KUnit-scoped; there is no filesystem persistence.

Dependencies and integration points: depends on DRM KUnit helpers, KUnit device registration, DRM mode config/framebuffer internals via `../drm_crtc_internal.h`, DRM fourcc metadata, format modifiers, and mode-object ID management. It covers central validation paths used by userspace framebuffer creation ioctls before driver-specific `fb_create` runs.

Risks: the create-case table encodes subtle legacy behavior: unused plane fields may be tolerated without `DRM_MODE_FB_MODIFIERS` but rejected with modifiers, and modifier arrays must be consistent for multi-plane formats. These rules are easy to regress when tightening validation. Tests use a mock `fb_create` that always returns `-EINVAL`, so they only assert validation reaches the callback, not successful framebuffer allocation. Lifecycle tests create stack framebuffers and depend on cleanup order to keep the mock mode-object/list state balanced. Large offset and overflow cases are important because integer arithmetic bugs can become memory safety issues in drivers.

Test signals: parameter descriptions identify the command scenario that failed. Regressions show up as unexpected callback delegation, wrong error for unsupported modifiers, incorrect `-ENOSPC` source-coordinate handling, list count mismatches after cleanup, missing lookup references, bad init refcount/type/free callback, or failure to call framebuffer destroy during free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_framebuffer_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_gem_shmem_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_gem_shmem_test.c

Purpose: tests GEM shmem helper behavior for object creation, PRIME import from scatter/gather tables, page pinning, virtual mapping, sg-table export, driver sg-table caching, madvise transitions, and purge behavior.

Important APIs/types/functions: the suite imports `EXPORTED_FOR_KUNIT_TESTING` symbols and uses wrappers generated by `KUNIT_DEFINE_ACTION_WRAPPER()` for `kfree`, `sg_free_table`, `drm_gem_shmem_free`, and `drm_gem_shmem_unpin` so cleanup actions have type-safe signatures. Tests call `drm_gem_shmem_create()`, `drm_gem_shmem_prime_import_sg_table()`, `to_drm_gem_shmem_obj()`, `drm_gem_shmem_pin()`, `drm_gem_shmem_unpin()`, `drm_gem_shmem_vmap()`, `drm_gem_shmem_vunmap()`, `drm_gem_shmem_get_sg_table()`, `drm_gem_shmem_get_pages_sgt()`, `drm_gem_shmem_madvise()`, `drm_gem_shmem_is_purgeable()`, and `drm_gem_shmem_purge()`. Fixture init allocates a DRM device with `DRIVER_GEM`.

Control flow: create testing allocates a 1 MiB shmem GEM object and checks size, shmem file, and funcs. Private/import testing builds a mock one-entry sg_table backed by KUnit memory, maps it for DMA, creates a mock dma-buf attachment, imports it, verifies no shmem file and that `shmem->sgt` points to the imported table, then lets `drm_gem_shmem_free()` own cleanup. Pin testing checks pages are NULL/use-count 0 before pin, populated/use-count 1 after pin, every page pointer is present, then unpin returns to NULL/use-count 0. Vmap testing maps the object, verifies `vaddr` and map state, writes `TEST_BYTE` across the full mapping through `iosys_map`, reads it back byte-by-byte, then unmaps. `get_sg_table` exports an sg_table from already pinned pages without caching it in `shmem->sgt`; `get_pages_sgt` pins and caches the sg_table in `shmem->sgt`. Madvise testing validates positive state update, then irreversible negative state. Purge testing requires positive madvise plus cached pages/sgt, verifies purgeability, purges, and expects pages/sgt cleared and `madv` set to -1.

State and persistence: tests mutate GEM object fields `base.size`, `base.filp`, `base.funcs`, `pages`, `pages_use_count`, `vaddr`, `vmap_use_count`, `sgt`, and `madv`. DMA mapping state is created for the mock sg_table in the PRIME import path. KUnit cleanup actions guard object freeing, unpinning, and sg_table cleanup, with actions removed when ownership transfers to shmem free. There is no disk persistence.

Dependencies and integration points: depends on DRM GEM/shmem helpers, DMA-BUF and DMA mapping APIs, scatterlist allocation, `iosys_map`, Linux size constants, and DRM KUnit device allocation. It validates helper contracts used by simple DRM drivers that back GEM objects with shmem and export/import PRIME buffers.

Risks: DMA mapping in the import test requires a valid device DMA mask and correct ownership transfer of the sg_table; mistakes can trigger debug-kernel warnings or double frees. Pin/vmap/purge tests rely on refcounts reaching zero after unpin/vunmap, so hidden extra references would be caught. Byte-by-byte verification over 1 MiB is thorough but relatively expensive for a unit test. Purge behavior depends on the precise `madv` state machine: once negative, it must not become positive again.

Test signals: failures identify object allocation/init regressions, imported sg_table ownership mistakes, page pin leaks, vmap refcount or memory access failures, sg_table length/caching errors, madvise state-machine regressions, and purge not clearing backing pages or sg tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_gem_shmem_test.c -->
