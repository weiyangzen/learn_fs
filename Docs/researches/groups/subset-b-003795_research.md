# Research: subset-b-003795

Grouped research for XP-Pen HID-BPF device programs and shared HID-BPF helper headers under `sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__Artist24.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__Artist24.bpf.c

Purpose: This HID-BPF program fixes XP-Pen Artist 24 and Artist 24 Pro USB tablet firmware behavior. It replaces the pen report descriptor so the second pen button is exposed as Secondary Barrel Switch instead of Eraser, then filters live reports that create false tip releases while the firmware tries to emulate an eraser-style button.

Important APIs/types/functions: `HID_BPF_CONFIG()` binds the program to UGEE vendor ID `0x28BD` and products `PID_ARTIST_24` and `PID_ARTIST_24_PRO`. `fixed_rdesc` is the replacement 107-byte report descriptor for report ID 7. `hid_fix_rdesc_xppen_artist24()` is the `HID_BPF_RDESC_FIXUP` entry point and writes `fixed_rdesc` through `hid_bpf_get_data()`. `xppen_24_fix_eraser()` is the `HID_BPF_DEVICE_EVENT` entry point. It uses button-state masks `TIP_SWITCH`, `BARREL_SWITCH`, `ERASER`, and `IN_RANGE`, plus the file-static `prev_state`. `HID_BPF_OPS(xppen_artist_24)` wires both callbacks into struct ops. `probe()` accepts only the intended 107-byte descriptor and rejects kernels or descriptors where byte 17 is no longer Eraser.

Control flow: At load/probe time, the syscall probe verifies descriptor size and the expected original eraser usage. During descriptor fixup, the program obtains mutable descriptor bytes and copies the replacement descriptor into the HID-BPF buffer, returning the new descriptor length. During input processing, it reads the first 10 report bytes, compares `data[1]` against `prev_state`, ignores unchanged state, detects illegal out-of-range transitions while the previous report had the tip down, updates `prev_state` for in-range reports, and suppresses reports where Tip Switch and Eraser changed together.

State and persistence: The only persistent program state is the global `prev_state`, which records the previous report's button/proximity bits across events. Descriptor changes are not stored in the program after fixup; they are handed back to the HID core. There is no map-backed state and no async work.

Dependencies and integration points: The program depends on `vmlinux.h`, `hid_bpf.h`, `hid_bpf_helpers.h`, libbpf tracing macros, HID-BPF kfuncs, and kernel-side struct-ops dispatch. It integrates with HID descriptor parsing, input event filtering, and userspace tablet applications that expect a barrel button rather than an eraser tool.

Risks: `prev_state` is global to the BPF object, so behavior assumes one relevant device instance or at least compatible state sharing. The filter intentionally cannot defer reports with a timer, so it treats some illegal transitions as false releases. Byte offsets in `fixed_rdesc`, `probe()`, and `data[1]` are tightly coupled to this firmware report layout. If a later kernel or firmware already fixes the descriptor, the probe guard should reject attachment, but offset drift could still cause missed fixes or wrong event suppression.

Test signals: Useful checks include successful attachment only on 107-byte descriptors with Eraser at byte 17, descriptor replacement length 107, report ID 7 pen motion and pressure still decoded, second barrel button exposed as BTN_STYLUS2 rather than eraser, no false tip-up events when pressing/releasing the second button while drawing, and no suppression of normal out-of-proximity events when the tip was not down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__Artist24.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__ArtistPro16Gen2.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__ArtistPro16Gen2.bpf.c

Purpose: This HID-BPF program fixes second-generation XP-Pen Artist Pro 14, 16, and 19 tablet displays. It replaces the flawed pen descriptor, repairs the eraser report semantics when the eraser button is pressed during contact, and compensates X/Y coordinates for tilt-dependent coil offset using per-device precomputed tables.

Important APIs/types/functions: `HID_BPF_CONFIG()` binds UGEE product IDs `0x095A`, `0x095B`, and `0x096A`. `fixed_rdesc` is a 113-byte replacement descriptor whose default physical dimensions match the 16-inch device. `hid_fix_rdesc_xppen_artistpro16gen2()` copies that descriptor and patches physical maximum bytes for 14-inch and 19-inch products. `xppen_16_fix_eraser()` converts the invalid Tip Switch plus Invert state into Eraser only by XORing bits `0x19`. The six `angle_offsets_*_{14,16,19}` tables encode tilt compensation for horizontal and vertical axes. `compensate_coordinates_by_tilt()` reads 16-bit little-endian coordinates, clamps compensation, and writes adjusted coordinates back. `xppen_16_fix_angle_offset()` selects the correct tables by product. `xppen_artist_pro_16_device_event()` runs tilt compensation first and eraser repair second.

Control flow: Probe rejects descriptors that are not 113 bytes or that no longer contain Eraser at descriptor byte 17. Descriptor fixup copies the canonical descriptor and optionally patches physical maximum fields based on `hctx->hid->product`. Runtime event flow obtains a 10-byte report, adjusts X and Y based on signed tilt bytes 8 and 9, then checks for the specific invalid button state `tip switch=1, invert=1, inrange=1` and toggles bits to report eraser without a tip switch.

State and persistence: The program has no mutable persistent state. All compensation tables and descriptors are static constants. Runtime changes are in-place edits of the current HID report buffer. Because no state is retained between events, coordinate correction is deterministic and only depends on current report bytes and product ID.

Dependencies and integration points: It depends on HID-BPF kfuncs from `hid_bpf_helpers.h`, struct-op section names from `hid_bpf.h`, and BPF verifier-friendly fixed arrays. It integrates with HID report descriptor parsing, Linux input tablet tool/button semantics, and calibration assumptions in userspace drawing software.

Risks: The replacement descriptor uses 16-inch defaults and byte-specific physical maximum patching for other products, so descriptor layout changes would break the patch offsets. The tilt compensation uses empirical tables and assumes logical max 32767; bad table values would create coordinate drift near screen edges. The eraser fix only handles one observed invalid bit pattern and may miss other firmware sequences. Large static tables increase BPF object size and verifier exposure, though the code path is straightforward.

Test signals: Validate attachment on all three product IDs, descriptor size 113, correct physical dimensions for 14/16/19-inch models, pressure maximum 16383, eraser button behavior during hover and contact, X/Y coordinate stability at positive and negative tilt, edge clamping at 0 and 32767, and no event mutation for nonmatching button states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__ArtistPro16Gen2.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__Deco01V3.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__Deco01V3.bpf.c

Purpose: This program normalizes XP-Pen Deco 01 V3 pad and pen HID behavior. It replaces the pad keyboard-style descriptor with a tablet-function-key descriptor, fixes the pen tilt logical range from -127..127 to -60..60, and converts incoming keyboard reports into a stable button bitmask.

Important APIs/types/functions: `HID_BPF_CONFIG()` matches UGEE product `PID_DECO_01_V3`. Constants define the pad descriptor length 102, pen descriptor length 109, pad report length 8, pad report ID 6, and eight pad buttons. `fixed_rdesc_pad` uses descriptor-construction macros from `hid_report_helpers.h` to describe a keypad/tablet-function-key collection with button state in byte 1, dummy tablet-pad fields, and padding. `xppen_deco01v3_rdesc_fixup()` handles both descriptor sizes: replacing the pad descriptor or patching two pen tilt ranges in-place. `xppen_deco01v3_device_event()` maps keyboard scan-code reports to a button mask.

Control flow: Probe accepts only 102-byte pad descriptors and 109-byte pen descriptors. During fixup, the pad descriptor is fully replaced. For the pen descriptor, two four-byte sequences at offsets 89 and 101 are compared against `{0x15, 0x81, 0x25, 0x7f}` and replaced with `{0x15, 0xc4, 0x25, 0x3c}` if present. During event processing, only report ID 6 is rewritten. The code derives button 3 from bit 2 in `data[1]` and scans bytes 2 through 7 for known key codes representing the other buttons, then writes `{ report_id, button_mask, 0, ... }` back over the report.

State and persistence: There is no persistent mutable state. The report descriptor fix persists in the HID device instance after fixup. Per-event state is local to `button_mask` and loop indexes. The `pad_buttons` array inside the event program is static const and used only for lookup.

Dependencies and integration points: The file depends on `hid_bpf.h`, `hid_bpf_helpers.h`, `hid_report_helpers.h`, and HID-BPF descriptor/event hooks. It integrates with the HID input stack by presenting the pad as tablet function keys rather than as an ordinary keyboard, which is important for libinput and userspace tablet configuration tools.

Risks: The code relies on exact descriptor sizes and hard-coded pen descriptor offsets. Button recognition depends on firmware keyboard codes and byte ordering; future firmware could emit different codes or modifier encodings. `sizeof(pad_buttons)` is safe because the element type is one byte, but the zero placeholder for button 3 means byte value zero is deliberately ignored and button 3 must continue to be inferred from `data[1]`. The replacement descriptor contains dummy fields to force tablet-pad classification, so changes in HID classification heuristics could affect behavior.

Test signals: Check that the pad no longer appears as a keyboard-only device, all eight buttons set stable bits under individual and combined presses, button 3 works through the modifier bit path, pen tilt reports are limited to -60..60, non-pad reports pass through unchanged, and the program rejects unrelated descriptor sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__Deco01V3.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__Deco02.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__Deco02.bpf.c

Purpose: This HID-BPF program fixes the XP-Pen Deco 02 main pad interface. It replaces a mixed pen/vendor/button/keyboard descriptor with a descriptor that preserves pen reporting while exposing pad buttons and the rotary dial as proper tablet-pad controls, then rewrites keyboard-style runtime reports into a dial byte and button bitmask.

Important APIs/types/functions: `HID_BPF_CONFIG()` matches UGEE product `PID_DECO_02`. Constants define the original 188-byte descriptor, 8-byte pad report, keyboard report ID 3, six button count, and the keyboard descriptor offset. `fixed_rdesc_pad` uses descriptor helper macros to create a pen collection followed by a fixed keypad/tablet-function-key collection. The fixed pad report uses byte 1 for relative `Usage_GD_Dial`, byte 2 for six buttons, byte 3 as a tablet-pad marker, bytes 4 and 5 for dummy X/Y fields, and bytes 6 and 7 as padding. `xppen_deco02_rdesc_fixup()` replaces the descriptor, and `xppen_deco02_device_event()` performs event conversion.

Control flow: Probe only accepts the 188-byte descriptor. The descriptor fixup copies `fixed_rdesc_pad` and returns its size. At runtime, reports that are missing or not report ID 3 pass through. For keyboard reports, bytes 2 through 7 are scanned. Key code `0x2e` becomes dial `+1`, `0x2d` becomes dial `-1`, and known key codes set bits for buttons 1 through 6. A new 8-byte report `{3, dial_code, button_mask, 0, ...}` replaces the original report.

State and persistence: There is no mutable state across reports. The dial is emitted as a relative single-event value based on the current keyboard click code, and button state is reconstructed from currently present key codes. Descriptor replacement persists through the HID device's parsed report layout.

Dependencies and integration points: The program depends on HID-BPF helpers, descriptor-generation macros, and HID input interpretation of relative dials and tablet pad buttons. It integrates with libinput/tablet userspace by preventing the pad from acting as a keyboard and by exposing the dial through a standard relative HID usage.

Risks: The report converter assumes the firmware's keyboard key codes for buttons and dial clicks remain fixed. It collapses any simultaneous clockwise and anticlockwise codes to the last scanned match, although the hardware should not produce both. The `BIT(05)` spelling is octal notation for decimal 5, so it currently sets the intended bit but is visually easy to misread. Replacement descriptor size and fields must remain compatible with the original 8-byte report payload.

Test signals: Validate that the stylus report still works after descriptor replacement, all six buttons are reported as tablet pad buttons under single and combined presses, the dial emits relative +1 and -1 events and returns to rest, keyboard events are no longer leaked to applications, unknown report IDs pass through, and descriptor attachment is limited to the 188-byte main interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__Deco02.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__DecoMini4.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__DecoMini4.bpf.c

Purpose: This HID-BPF program fixes XP-Pen Deco Mini 4 compatibility-mode pad and pen interfaces. It replaces pad and pen report descriptors with tablet-appropriate descriptors, uses vendor-provided logical/physical maximums for the pen, and converts keyboard-like pad reports into a six-button mask.

Important APIs/types/functions: `HID_BPF_CONFIG()` matches UGEE product `PID_DECO_MINI_4`. Constants define pad descriptor size 177, pen descriptor size 109, pad report ID 6, logical X/Y maxima, calculated physical X/Y maxima, and pressure maximum 8191. `pad_buttons` maps firmware key codes for buttons 1, 2, 4, 5, and 6, with button 3 inferred from a modifier bit. `fixed_pad_rdesc` is a compact tablet-function-key descriptor. `fixed_pen_rdesc` describes a stylus report with tip, barrel, tablet pick, in-range, X/Y coordinates, pressure, and padding. `hid_rdesc_fixup_xppen_deco_mini_4()` selects the replacement descriptor by input descriptor size. `hid_device_event_xppen_deco_mini_4()` rewrites pad reports into button masks.

Control flow: Probe accepts the two compatibility-mode descriptor sizes and rejects other interfaces, including the raw-mode-only interface. Descriptor fixup copies the fixed pad or pen descriptor and returns its size. Event processing reads 8 bytes, ignores non-pad report IDs, sets button 3 from bit 2 of `data[1]`, scans bytes 2 through 7 for matching key codes in `pad_buttons`, and writes a normalized report with byte 1 as the button mask.

State and persistence: No mutable global or map state is used. The selected fixed descriptor persists in the HID core after fixup. Per-report state is transient and consists of the computed `button_mask`.

Dependencies and integration points: The program depends on HID-BPF kfunc access to descriptor and report buffers, HID report semantics for tablet function keys and stylus axes, and userspace tablet stacks that expect pad buttons rather than keyboard shortcuts. It integrates with compatibility mode and intentionally does not switch the tablet into raw mode.

Risks: The descriptor constants encode values from a device query comment; if firmware changes resolution or maxima, coordinates and pressure may be misdeclared. Raw mode is out of scope, so users expecting raw-mode behavior need a different program. Button decoding has the same modifier-bit dependency as related XP-Pen pad fixups. The replacement pad descriptor has many padding bits, so report-length compatibility should be checked carefully.

Test signals: Validate descriptor replacement on both pad and pen interfaces, rejection of unrelated descriptor sizes, correct pen coordinate maxima and pressure maximum, all six pad buttons under single and multi-button presses, button 3 modifier-bit handling, no keyboard shortcut leakage, and unchanged behavior for non-pad reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__DecoMini4.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_bpf.h -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_bpf.h

Purpose: This small public header defines the section names, struct-op declaration helper, simple device-name helper, and probe argument structure shared by HID-BPF programs in this directory.

Important APIs/types/functions: `HID_BPF_DEVICE_EVENT` expands to `struct_ops/hid_device_event`, and `HID_BPF_RDESC_FIXUP` expands to `struct_ops/hid_rdesc_fixup`; programs use these names in `SEC()` annotations. `HID_BPF_OPS(name)` declares a linked `.struct_ops.link` `struct hid_bpf_ops` object. `hid_set_name(_hdev, _name)` copies a compile-time string into `hdev->name`. `struct hid_bpf_probe_args` carries the HID identifier, report descriptor size, up to 4096 descriptor bytes, and a `retval` field set by syscall-style probe programs.

Control flow: The header has no runtime flow itself. It shapes how BPF object files expose callbacks. A typical program defines descriptor and/or event functions in the section names, creates a `HID_BPF_OPS()` object assigning those callbacks, and defines `probe()` in the `syscall` section to accept or reject a device.

State and persistence: The header stores no state. `hid_bpf_probe_args` is transient per probe invocation. `HID_BPF_OPS()` creates static BPF object metadata that persists as part of the loaded BPF program.

Dependencies and integration points: It depends on `struct hid_bpf_ops` and HID objects from `vmlinux.h` included by users. It is the local ABI glue between BPF C source files, libbpf section loading, and kernel HID-BPF struct-ops registration.

Risks: Section-name strings are contract-sensitive; changing them would break loader/kernel attachment. `hid_set_name()` copies `sizeof(_name)` bytes, so it is intended for fixed arrays or string literals and can be wrong for pointers. The probe descriptor buffer is fixed at 4096 bytes, matching `HID_MAX_DESCRIPTOR_SIZE` in helpers, and code should not assume larger descriptors are available.

Test signals: Build HID-BPF programs using the macros, inspect BTF/ELF sections for `.struct_ops.link` and expected callback sections, validate probe programs can read `rdesc_size` and set `retval`, and confirm no duplicate or mismatched struct-op symbols are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_bpf_async.h -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_bpf_async.h

Purpose: This header provides a reusable HID-BPF async execution framework built on BPF timers and BPF workqueues. It lets HID-BPF programs schedule immediate or delayed callbacks that reacquire a HID-BPF context by HID device ID and then run normal context-based helper code outside the original event path.

Important APIs/types/functions: Users must define `HID_BPF_ASYNC_MAX_CTX` before including the header. `enum hid_bpf_async_state` tracks context lifecycle from unset through initialized, starting, and running. `struct hid_bpf_async_map_elem` contains a `bpf_spin_lock`, state, `bpf_timer`, `bpf_wq`, and HID ID. `hid_bpf_async_ctx_map` is a global BPF array map sized by `HID_BPF_ASYNC_MAX_CTX`. `HID_BPF_ASYNC_CB(cb)` wraps a workqueue callback around `hid_bpf_allocate_context()` and `hid_bpf_release_context()`. `HID_BPF_ASYNC_FUN(fun)`, `HID_BPF_ASYNC_INIT(fun)`, and `HID_BPF_ASYNC_DELAYED_CALL(fun, ctx, delay)` provide a higher-level function declaration, one-time allocation, and delayed scheduling pattern. Lower-level helpers include `hid_bpf_async_get_ctx()`, `hid_bpf_async_delayed_call()`, `hid_bpf_async_call()`, and `ms_to_ns()`.

Control flow: Initialization scans the async map for an `UNSET` slot under a spinlock, moves it to `INITIALIZING`, initializes a timer and workqueue, and marks it `INITIALIZED`. A delayed call looks up the reserved key, verifies the state is `INITIALIZED` or `RUNNING`, marks it `STARTING`, stores the current HID ID, sets the workqueue callback, and either starts a timer or starts the workqueue immediately. Timer expiry runs `__start_wq_timer_cb()`, which starts the workqueue. The generated workqueue wrapper allocates a fresh HID-BPF context, marks state `RUNNING`, invokes the user callback, resets state to `INITIALIZED`, and releases the context.

State and persistence: Persistent state lives in `hid_bpf_async_ctx_map`. Each slot retains lock, state, initialized timer/workqueue objects, and the most recent HID ID. The state machine prevents uninitialized or concurrently starting slots from being reused, but it does not store per-call payload beyond HID ID and callback selection.

Dependencies and integration points: The header depends on BPF map declarations, `bpf_timer_*`, `bpf_wq_*` kfuncs, BPF spin locks, `hid_bpf_allocate_context()`, and `hid_bpf_release_context()` from `hid_bpf_helpers.h`. It integrates with HID-BPF programs that need delayed hardware requests, retries, or report injection that cannot be performed synchronously in the original callback.

Risks: Callers must reserve enough slots and call `HID_BPF_ASYNC_INIT()` before scheduling; otherwise calls fail with negative errors. Error paths during timer/workqueue initialization can leave a slot in `INITIALIZING` rather than returning it to `UNSET`. A slot stores only one HID ID and callback setup at a time, so overlapping scheduling on the same key can race or return `-EINVAL`. Callback code runs with a newly allocated context and must handle allocation failure. Kernel support for weak workqueue kfuncs is required.

Test signals: Compile with a defined `HID_BPF_ASYNC_MAX_CTX`, verify slot allocation exhaustion behavior, exercise immediate and delayed callbacks, confirm state transitions return to `INITIALIZED`, confirm context allocation failures do not leak references, test re-entry from a running callback, and test behavior on kernels without required BPF workqueue support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_bpf_async.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_bpf_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_bpf_helpers.h

Purpose: This shared helper header is the main support library for HID-BPF programs. It declares HID-BPF kfuncs, workqueue kfuncs, common constants, cleanup/guard macros, HID device matching macros, endian helpers, udev property helpers, and verifier-friendly helpers for inspecting parsed HID report descriptors.

Important APIs/types/functions: Kfunc declarations include `hid_bpf_get_data()`, `hid_bpf_allocate_context()`, `hid_bpf_release_context()`, `hid_bpf_hw_request()`, `hid_bpf_hw_output_report()`, `hid_bpf_input_report()`, and `hid_bpf_try_input_report()`. Weak workqueue declarations include `bpf_wq_init()`, `bpf_wq_start()`, and `bpf_wq_set_callback()`. Core constants include `HID_MAX_DESCRIPTOR_SIZE`, `HID_IGNORE_EVENT`, bus IDs, HID group IDs, `HID_VID_ANY`, `HID_PID_ANY`, `BIT()`, and `ARRAY_SIZE()`. Cleanup helpers provide `_cleanup_`, `_release_`, `DEFINE_RELEASE_CLEANUP_FUNC()`, and a release helper for `hid_bpf_ctx`. `DEFINE_GUARD()` and `guard(bpf_spin)` implement scoped BPF spinlock cleanup. `HID_DEVICE()` and `HID_BPF_CONFIG()` emit BTF-readable device ID metadata in `.hid_bpf_config`. Endian helpers provide HID little-endian conversions. `EXPORT_UDEV_PROP()`, `udev_prop_ptr()`, and `UDEV_PROP_SPRINTF()` expose udev properties through BPF maps. Descriptor helpers include `field_start_byte()`, `field_end_byte()`, `extract_bits()`, `EXTRACT_BITS()`, and `hid_bpf_for_each_*` iterator macros for reports, fields, and collections.

Control flow: Most content is compile-time macro expansion. At runtime, helper users call kfuncs to access report buffers, issue hardware requests, inject input, or allocate contexts. `extract_bits()` calculates byte bounds and either uses fast paths for aligned 8/16/32-bit reads or a bounded `bpf_for` loop for general bitfields. Iterator macros wrap `bpf_iter_num` with bounds checks so descriptor traversal remains verifier-friendly. `HID_BPF_CONFIG()` uses argument-counting macros to build a union of anonymous `HID_DEVICE()` entries for loader introspection.

State and persistence: The header itself owns no mutable state except maps created by `EXPORT_UDEV_PROP()` in including programs. Generated HID configuration metadata persists in the BPF object. Cleanup and guard macros create scoped local variables whose cleanup attributes release contexts or unlock spin locks at scope exit.

Dependencies and integration points: It depends on `vmlinux.h`, libbpf helper headers, BPF endian helpers, Linux errno values, and local `hid_report_descriptor_helpers.h`. It is included by nearly all HID-BPF programs in the directory and forms the local compatibility layer between BPF C code, libbpf, BTF introspection, and kernel HID-BPF helper APIs.

Risks: Macro-heavy code is sensitive to compiler and verifier behavior. `HID_BPF_CONFIG()` supports only up to 15 device entries unless its countdown and argument macros are extended. `BIT(n)` uses `1UL`, so callers must be careful with large bit indexes and target word size. `extract_bits()` supports at most 32-bit fields and returns 0 for invalid bounds, which can hide malformed descriptors if callers do not distinguish error from value zero. Cleanup and guard macros depend on compiler cleanup attributes accepted by the BPF build pipeline.

Test signals: Build coverage across many HID-BPF programs, BTF inspection of `.hid_bpf_config`, verifier acceptance of `extract_bits()` and iterator macros, endian tests on little and big endian builds, scoped spinlock cleanup paths, udev property map emission, and runtime checks for report buffer access and `HID_IGNORE_EVENT` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_bpf_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_report_descriptor_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_report_descriptor_helpers.h

Purpose: This header defines compact, BPF-friendly data structures for parsed HID report descriptors. The structures let HID-BPF programs reason about reports, fields, collections, usages, logical ranges, and field flags without parsing raw descriptor bytes themselves.

Important APIs/types/functions: `HID_MAX_COLLECTIONS`, `HID_MAX_FIELDS`, and `HID_MAX_REPORTS` bound descriptor representation sizes. `enum hid_rdesc_field_type` distinguishes variable, array, and constant fields. `struct hid_rdesc_collection` stores usage page, usage ID, and collection type. `struct hid_rdesc_field` stores field type, collection count, bit start/end offsets, usage page, variable usage ID or array usage min/max, signed logical min/max, flag bits for relative/wrap/nonlinear/no-preferred/null/volatile/buffered/reserved, and an inline array of collections. `struct hid_rdesc_report` stores report ID, size in bits, field count, and field array. `struct hid_rdesc_descriptor` stores counts and arrays for input, output, and feature reports.

Control flow: There is no executable control flow in this file. It provides packed layout definitions consumed by helper functions and HID-BPF programs that receive or store parsed descriptor data.

State and persistence: The header has no global state. Instances of these structs may be produced by parser code elsewhere or embedded in maps/program data by HID-BPF users. Fields are packed to keep ABI layout stable and compact for BPF access.

Dependencies and integration points: It depends on integer types from `vmlinux.h` and compiler attributes. `hid_bpf_helpers.h` uses these definitions for `field_start_byte()`, `field_end_byte()`, `extract_bits()`, and descriptor iterator macros. Programs that inspect descriptor semantics rely on the max-count constants matching parser output and verifier loop bounds.

Risks: Fixed maximum counts can truncate complex descriptors if parser code does not report overflow clearly. Packed structs may create unaligned access concerns on some targets, so generated BPF access patterns need compiler/verifier coverage. The flag bit for `is_volatile` is documented as not populated and always zero, which callers must not treat as authoritative output/feature volatility. Any ABI drift between parser producers and these structures would break descriptor introspection.

Test signals: Compile-time size/layout checks, parser tests for descriptors with many reports/fields/collections, iterator tests that respect maximum counts, field bit-offset extraction tests, and big/little endian build coverage for consumers that read packed integer fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_report_descriptor_helpers.h -->
