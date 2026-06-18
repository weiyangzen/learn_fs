# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params.c

Purpose: discovers, constructs, logs, and cleans UC-Logic-family tablet interface parameters. It is the model-specific decision table behind the UC-Logic core driver, translating USB IDs, interface numbers, string descriptors, magic probe sequences, and quirks into declarative pen/frame/battery/event-hook configuration.

Important APIs, types, and functions: exported helpers are `uclogic_params_init()`, `uclogic_params_get_desc()`, `uclogic_params_cleanup()`, and `uclogic_params_hid_dbg()`. Internal paths include `uclogic_params_get_str_desc()` for raw USB string descriptors, `uclogic_params_pen_init_v1()` and `_v2()` for Huion-style pen descriptors, `uclogic_params_frame_init_with_desc()` and `_v1()` for frame descriptors, `uclogic_params_parse_ugee_v2_desc()` for UGEE v2 descriptor parsing, `uclogic_probe_interface()` for magic interrupt probing, UGEE v2 frame/battery/event-hook helpers, and `uclogic_params_init_ugee_xppen_pro()` for Artist 22R/24 Pro special handling.

Control flow: `uclogic_params_init()` validates USB HID, extracts device and interface metadata, then switches on VID/PID. Some devices receive static descriptor replacements guarded by original descriptor size. Others probe pen parameters from string descriptors, mark non-useful interfaces invalid, or initialize UGEE v2 devices by sending magic data before reading descriptor 100. Output is copied from a temporary `struct uclogic_params` into the caller, with cleanup on errors.

State and persistence: all descriptor parts are kmalloc-owned and later freed by `uclogic_params_cleanup()`. Event hooks own event byte copies and work structs; cleanup cancels work and is idempotent. Firmware strings may populate `hdev->uniq`, and battery devices rewrite `hdev->uniq` to vendor-product form for hwmon safety. No disk persistence.

Dependencies and integration: depends on USB control/interrupt messaging, unaligned access helpers, `hid-uclogic-rdesc` descriptor templates, and `hid-ids.h`. The core driver consumes the resulting parameter structure for report fixup and raw-event transforms.

Risks: this file is heavily hardware-protocol dependent. Incorrect descriptor sizes, interface assumptions, or string parsing can disable interfaces or build wrong descriptors. Several paths return invalid/noop intentionally, so error handling must distinguish unsupported hardware from real failures. Event-hook initialization has multi-allocation cleanup risk; KUnit covers repeated cleanup.

Test signals: includes `hid-uclogic-params-test.c` under HID KUnit. Additional validation needs real tablets across static descriptor, Huion v1/v2, UGEE v2, battery, wireless reconnect, and XP-PEN Pro paths.
