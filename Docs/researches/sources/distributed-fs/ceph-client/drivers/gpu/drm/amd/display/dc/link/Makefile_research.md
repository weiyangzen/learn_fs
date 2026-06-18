# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/Makefile

Purpose: Kbuild fragment listing AMD display core link subcomponent object files and adding them to `AMD_DISPLAY_FILES`.

Important APIs/types/functions: defines object groups `LINK`, `LINK_ACCESSORIES`, `LINK_HWSS`, and `LINK_PROTOCOLS`; expands each through `$(addprefix $(AMDDALPATH)/dc/link/, ...)`; appends generated object paths to `AMD_DISPLAY_FILES`.

Control flow and integration: the parent AMD display build includes this Makefile so link detection, DPMS, resource, validation, accessories (`link_dp_trace.o`, `link_dp_cts.o`), hardware sequencing, and protocol modules are compiled into the driver.

State and persistence: build metadata only; no runtime state.

Dependencies and risks: depends on parent variables `AMDDALPATH` and `AMD_DISPLAY_FILES`. Missing an object here can compile out required link functionality; adding an object with missing source or unmet config guards breaks the driver build.

Test signals: kernel/driver build, link-time symbol resolution, and confirming new link module source files are represented in the correct object group.
