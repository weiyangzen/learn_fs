# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hdcp/Makefile

Purpose: Adds the HDCP message transport object to the AMD display build.

Important APIs and build variables: `HDCP_MSG = hdcp_msg.o` names the object. `AMD_DAL_HDCP_MSG` prefixes it with `$(AMDDALPATH)/dc/hdcp/`. `AMD_DISPLAY_FILES += $(AMD_DAL_HDCP_MSG)` injects it into the display object list.

Control flow: this Makefile is included by the larger AMD display make hierarchy. There are no conditionals in this file, so inclusion depends on the parent build logic rather than local guards.

State and persistence: no runtime state. Build state is limited to make variables.

Dependencies and integration: integrates `hdcp_msg.c` with the display driver. It assumes `AMDDALPATH` and `AMD_DISPLAY_FILES` are defined by parent makefiles.

Risks and test signals: missing parent inclusion or wrong path prefix would silently omit HDCP message support. Build tests should confirm `hdcp_msg.o` appears in the final object list for configurations that enable AMD DC.
