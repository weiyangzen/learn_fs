# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_client_modeset_test.c

## Purpose

`drm_client_modeset_test.c` provides KUnit tests for command-line mode selection in DRM client modeset helpers. It verifies that parsed command-line modes pick the expected probed display mode for explicit resolution/refresh and for named analog TV modes.

## Important APIs, Types, and Functions

- `struct drm_client_modeset_test_priv` stores a test DRM device, backing device, and connector.
- `drm_client_modeset_connector_get_modes()` supplies probed modes: no-EDID modes up to 1920x1200 plus analog NTSC 480i and PAL 576i modes.
- `drm_client_modeset_test_init()` allocates the test DRM device and connector, installs helper funcs, and allows interlace/doublescan.
- `drm_test_pick_cmdline_res_1920_1080_60()` parses `1920x1080@60`, probes modes, and expects DMT 1920x1080@60.
- `drm_test_pick_cmdline_named()` is parameterized for `NTSC`, `NTSC-J`, `PAL`, and `PAL-M`.

## Control Flow

Each test parses a command-line mode into `connector->cmdline_mode`, locks the mode-config mutex, probes connector modes with `drm_helper_probe_single_connector_modes()`, unlocks, calls `drm_connector_pick_cmdline_mode()`, and compares the selected mode with an expected DRM mode. The named-mode tests generate expected modes through analog mode helpers.

## State and Persistence Behavior

The test connector stores parsed cmdline mode state and probed modes for the duration of each test. KUnit cleanup handles allocated modes through `drm_kunit_add_mode_destroy_action()` and test device cleanup.

## Dependencies and Integration Points

The file depends on KUnit, DRM connector, EDID/mode helpers, DRM driver allocation helpers, modeset helper vtables, and probe helpers. It is included directly by `drm_client_modeset.c`, so it deliberately avoids `MODULE_*` macros.

## Risks and Edge Cases

- It is built by inclusion rather than as a normal standalone test module source, so include ordering and symbol visibility depend on `drm_client_modeset.c`.
- Coverage is limited to successful mode picking; malformed command lines are covered in the separate parser tests.
- The connector type is unknown, but analog named modes are supplied by the helper get-modes function.

## Test Signals

The `drm_test_pick_cmdline` KUnit suite should pass, selecting DMT 1920x1080@60 for the explicit command line and matching NTSC/PAL helper modes for named command lines.
