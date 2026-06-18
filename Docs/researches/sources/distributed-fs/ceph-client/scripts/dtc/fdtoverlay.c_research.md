# sources/distributed-fs/ceph-client/scripts/dtc/fdtoverlay.c

Purpose: command-line utility that applies one or more compiled device-tree overlays (`.dtbo`) to a base DTB and writes a packed output DTB. It is a thin orchestration layer over libfdt overlay APIs.

Important APIs/functions: `main()` parses `-i`, `-o`, `-v` via `util_getopt_long`; `do_fdtoverlay()` reads the base and overlay blobs with `utilfdt_read`, validates read lengths against `fdt_totalsize`, applies overlays sequentially, packs with `fdt_pack`, and writes with `utilfdt_write`; `apply_one()` expands a working buffer in 64 KiB increments, copies the overlay because `fdt_overlay_apply()` invalidates inputs on failure, checks whether the base has `/__symbols__`, and retries only on `-FDT_ERR_NOSPACE`.

Control flow/state: the current base blob pointer is replaced after each successful overlay. `buf_len` persists as the mutable capacity across overlays. On success ownership of the old base is freed; on failure temporary base/overlay copies are freed and the original call unwinds.

Dependencies/integration: depends on `libfdt.h` for `fdt_open_into`, `fdt_overlay_apply`, `fdt_path_offset`, `fdt_pack`, `fdt_strerror`; on `util.h` for I/O, allocation, and common usage handling. It is an end-user wrapper around `libfdt/fdt_overlay.c`.

Risks: failure paths must assume both base and overlay may be corrupted, hence the copy discipline is important. Missing base symbols produce confusing overlay fixup failures, so the explicit `-@` diagnostic is important. `verbose` is global but only affects CLI printing here.

Test signals: exercise applying overlays with phandle and path targets, insufficient output space retry, missing `/__symbols__` diagnostics, incomplete blob read rejection, multi-overlay sequencing, and output repacking.
