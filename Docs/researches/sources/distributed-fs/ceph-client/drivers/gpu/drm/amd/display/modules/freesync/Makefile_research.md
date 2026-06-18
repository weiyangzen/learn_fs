# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/freesync/Makefile

Purpose: Adds the FreeSync module object to the AMD display build. It defines `FREESYNC = freesync.o`, prefixes it with `$(AMDDALPATH)/modules/freesync/`, and appends it to `AMD_DISPLAY_FILES`.

Important APIs and types: Build variables `FREESYNC`, `AMD_DAL_FREESYNC`, and `AMD_DISPLAY_FILES`. There are no runtime APIs.

Control flow: Included by the parent AMD display Makefile so `freesync.o` is compiled and linked into the driver.

State and persistence: Build-time make variable state only.

Dependencies and integration points: Depends on parent Makefile definitions and on `freesync.c` satisfying the `mod_freesync` API expected by DC/DM.

Risks: Missing this object causes unresolved FreeSync symbols or disabled VRR behavior. Incorrect `AMDDALPATH` breaks object path expansion.

Test signals: Full AMD display build and link resolution for `mod_freesync_*` entry points.
