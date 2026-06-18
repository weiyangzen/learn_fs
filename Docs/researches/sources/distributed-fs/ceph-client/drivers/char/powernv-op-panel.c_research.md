# sources/distributed-fs/ceph-client/drivers/char/powernv-op-panel.c

## Purpose
`powernv-op-panel.c` exposes IBM PowerNV OPAL operator-panel LCD displays as `/dev/op_panel`. Userspace can read the cached display buffer or write text that is sent to firmware for display on the physical operator panel.

## Important APIs, Types, and Functions
- `oppanel_probe()` reads device-tree properties `#length` and `#lines`, allocates `oppanel_data` and `oppanel_lines`, initializes line descriptors with physical addresses, and registers a dynamic misc device.
- `oppanel_write()` writes into the cached buffer with `simple_write_to_buffer()` and calls `__op_panel_update_display()`.
- `__op_panel_update_display()` obtains an OPAL async token, calls `opal_write_oppanel_async()`, waits for async completion when required, reads the async result, and releases the token.
- `oppanel_open()` uses `mutex_trylock()` to enforce a single opener; `oppanel_release()` unlocks.
- `oppanel_llseek()` and `oppanel_read()` use fixed-size/simple buffer helpers.

## Control Flow
The platform driver binds to `ibm,opal-oppanel`. Probe sizes the panel, allocates a space-filled buffer, builds per-line OPAL descriptors, and registers `/dev/op_panel`. On a write at offset zero, the whole cached panel buffer is cleared to spaces before applying new data. A successful buffer write triggers a firmware update; failure restores the previous file offset and returns `-EIO`.

## State and Persistence
Software state is global: `num_lines`, `oppanel_size`, `oppanel_lines`, and `oppanel_data`. The physical operator panel display persists outside the process and reflects the last successful OPAL update. Single-open locking prevents concurrent userspace writers/readers through this device.

## Dependencies and Integration Points
The file depends on Open Firmware device-tree matching, OPAL async APIs, misc core, physical address translation via `__pa()`, and platform-driver lifecycle. It is PowerNV-specific and requires firmware support for `opal_write_oppanel_async()`.

## Risks
- `oppanel_lines` stores physical addresses of allocated kernel memory; memory lifetime must span all firmware uses.
- The driver has global state and supports one device instance only.
- OPAL async failures convert to generic `-EIO`, and display/cache divergence is possible if firmware partially updates.
- Buffer formatting is raw; userspace must understand panel line size.

## Test Signals
Tests should cover missing DT properties, allocation failure unwind, single-open `-EBUSY`, fixed-size seek/read/write bounds, successful OPAL async and synchronous paths, and error handling that restores `f_pos` after failed firmware update.
