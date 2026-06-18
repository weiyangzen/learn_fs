# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/color/Makefile

Purpose: Adds the DAL color submodule objects to the AMD display build. It defines `MOD_COLOR = color_gamma.o color_table.o`, prefixes them with `$(AMDDALPATH)/modules/color/`, and appends the resulting paths to `AMD_DISPLAY_FILES`.

Important APIs and types: Build variables `MOD_COLOR`, `AMD_DAL_MOD_COLOR`, and `AMD_DISPLAY_FILES` are the only exported interface. There are no C APIs.

Control flow: During kernel build, the parent AMD display Makefile includes this file, expands object paths, and links `color_gamma.o` plus `color_table.o` into the display driver object set.

State and persistence: Build-only state through make variables. No runtime persistence.

Dependencies and integration points: Depends on the parent build defining `AMDDALPATH` and consuming `AMD_DISPLAY_FILES`. Integrates the transfer-function implementation and PQ/de-PQ table storage.

Risks: Omitting either object breaks public functions from `color_gamma.h`/`color_table.h`. Object path construction depends on correct `AMDDALPATH`. The commented debug `$(info ...)` is inert.

Test signals: Build success for AMD display with color module enabled and link resolution for `mod_color_calculate_*` and table functions.
