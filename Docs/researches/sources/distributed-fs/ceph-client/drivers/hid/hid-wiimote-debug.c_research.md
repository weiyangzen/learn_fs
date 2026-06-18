# sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-debug.c

## Purpose

`hid-wiimote-debug.c` provides optional debugfs controls for Wiimote devices. It exposes EEPROM reads and lets developers view or force the current data-report mode (DRM), which is useful when diagnosing extension and report-layout behavior.

## Important APIs, Types, and Functions

- `struct wiimote_debug`: stores the owning `wiimote_data` and debugfs dentries.
- `wiidebug_eeprom_read`: reads up to 16 EEPROM bytes at the file offset using the synchronous command path.
- `wiidebug_drm_show` and `wiidebug_drm_write`: expose the active DRM as a symbolic string and allow writing either a symbolic name or hex value.
- `wiidebug_init` and `wiidebug_deinit`: allocate/remove debug state and attach it to `wdata->debug`.

## Control Flow

`wiidebug_init` creates `eeprom` and `drm` files under the HID device debug directory. EEPROM reads acquire `state.sync`, set `cmd_read_buf` to a stack buffer, queue an EEPROM read request, wait for completion, clear the buffer pointer, and copy data to userspace. DRM writes parse the user string, clear `WIIPROTO_FLAG_DRM_LOCKED`, request the new DRM, and set the lock flag for non-null modes so automatic mode selection stops overriding it.

## State and Persistence Behavior

The debug object persists for the device lifetime and is removed before the Wiimote core tears down protocol state. The DRM debug file mutates persistent protocol flags and `state.drm`; EEPROM reads only use transient command state.

## Dependencies and Integration Points

This file depends on `CONFIG_DEBUG_FS`, debugfs, seq_file helpers, user-copy helpers, and the synchronous command APIs from `hid-wiimote.h`/core. The header provides no-op inline replacements when debugfs is disabled.

## Risks and Edge Cases

- `wiidebug_drm_write` compares the raw copied buffer with DRM names; trailing newlines from shell writes may not match names and will fall back to numeric parsing.
- EEPROM reads use a 16-byte stack buffer and expose only one chunk at a time by design.
- Forcing DRM can make normal module handlers receive incompatible payload layouts until DRM is unlocked.
- Debugfs creation failures are not checked per file; missing dentries may be tolerated but reduce diagnostics.

## Test Signals

- With debugfs enabled, verify `eeprom` offsets advance and stop past `0xffffff`.
- Write known DRM names and numeric values, then confirm `drm` output and report layout changes.
- Remove the device while debugfs files are open to check teardown safety.
- Confirm builds with and without `CONFIG_DEBUG_FS`.
