# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/Makefile

Purpose: adds the power-helper module object to the AMD display build.

Important APIs/build variables: defines `MOD_POWER = power_helpers.o`, builds `AMD_DAL_MOD_POWER` with the `$(AMDDALPATH)/modules/power/` prefix, and appends it to `AMD_DISPLAY_FILES`.

Control flow: build-only fragment; it ensures `power_helpers.c` is compiled into the display driver when the parent make hierarchy includes this module.

State and persistence: no runtime state. Persistent effect is the build object list contribution.

Dependencies and integration: relies on parent make variables and provides the implementation for declarations in `modules/power/power_helpers.h`.

Risks: new power module sources require manual list updates. Incorrect `AMDDALPATH` or missing inclusion will omit ABM/PSR/Replay helper implementations.

Test signals: full AMD display build includes `modules/power/power_helpers.o`, incremental rebuild after helper edits, and parent makefile expansion validation.
