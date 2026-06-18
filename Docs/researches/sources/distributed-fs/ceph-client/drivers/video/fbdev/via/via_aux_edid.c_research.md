<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_edid.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_edid.c

Purpose: Generic EDID auxiliary driver. It reads monitor EDID over DDC, converts it into fbdev monitor specs, keeps modedb private data, and exposes the first detailed mode as a preferred mode.

Important APIs/types/functions: `query_edid()` reads 128 bytes from address `0x50`, calls `fb_edid_to_monspecs()`, validates version/revision, replaces any prior modedb, and stores `struct fb_monspecs` in `drv->data`. `get_preferred_mode()` returns the first mode marked both `FB_MODE_IS_FIRST` and `FB_MODE_IS_DETAILED` when `FB_MISC_1ST_DETAIL` is present. `cleanup()` destroys the modedb. `via_aux_edid_probe()` always adds an EDID driver descriptor after an initial query.

Control flow and state: Unlike chip probes, EDID always installs a driver so connected/disconnected displays can be represented by a descriptor even if the first read fails. The only persistent state is the allocated `fb_monspecs` and its mode database. Cleanup intentionally frees the modedb but the descriptor's `data` allocation is released by `via_aux_free()`.

Dependencies and integration points: Depends on `../edid.h`, fb EDID helpers, and `via_aux_read()`. `viafbdev.c` uses `via_aux_get_preferred_mode()` to choose a default mode for CRT/DVP1 when module parameters are absent. Risks include single-shot EDID query with no hotplug refresh in this file, accepting only first detailed mode as preferred, no checksum reporting beyond fb helper behavior, and possible NULL mode if the monitor does not set the expected flags. Test signals are monitors with valid/invalid EDID, no-display DDC reads, preferred-mode fallback, and leak checks around repeated bus free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_aux_edid.c -->
