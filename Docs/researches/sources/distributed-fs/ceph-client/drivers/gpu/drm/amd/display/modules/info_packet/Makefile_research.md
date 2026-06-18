# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/info_packet/Makefile

Purpose: adds the info-packet module object to the AMD display build.

Important APIs/build variables: defines `INFO_PACKET = info_packet.o`, builds `AMD_DAL_INFO_PACKET` by prefixing `$(AMDDALPATH)/modules/info_packet/`, and appends it to `AMD_DISPLAY_FILES`.

Control flow: no runtime control flow. At build time, the display make hierarchy includes this fragment so `info_packet.c` is compiled and linked into the AMD display module.

State and persistence: no runtime state. The file participates in persistent build configuration through `AMD_DISPLAY_FILES`.

Dependencies and integration: depends on the parent make environment defining `AMDDALPATH` and `AMD_DISPLAY_FILES`. The object provides implementations declared in `modules/inc/mod_info_packet.h`.

Risks: path prefix errors or missing inclusion from parent makefiles would silently omit packet builders. Adding new source files in this directory requires updating this list.

Test signals: kernel/display build includes `modules/info_packet/info_packet.o`; clean builds and incremental builds after editing `info_packet.c`; parent makefile variable expansion for `AMDDALPATH`.
