# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/Makefile

Purpose: Adds HDCP module objects to the AMD display build, covering DDC transport, logging, PSP integration, top-level state management, and HDCP 1.x/2.x execution/transition logic.

Important APIs and types: `HDCP` lists `hdcp_ddc.o`, `hdcp_log.o`, `hdcp_psp.o`, `hdcp.o`, `hdcp1_execution.o`, `hdcp1_transition.o`, `hdcp2_execution.o`, and `hdcp2_transition.o`. `AMD_DAL_HDCP` prefixes them with `$(AMDDALPATH)/modules/hdcp/`, then appends to `AMD_DISPLAY_FILES`.

Control flow: Parent build includes this Makefile and links all HDCP components together. The split object list mirrors the module architecture: transport, secure processor operations, state execution, and state transitions.

State and persistence: Build-time make variables only.

Dependencies and integration points: Depends on `AMDDALPATH` and parent AMD display build infrastructure. Provides symbols declared by `hdcp.h` and public `mod_hdcp.h`.

Risks: Omitting any listed object breaks either HDCP 1.x/2.x, DP/HDMI transitions, PSP calls, DDC messages, or logging. Build ordering is simple but symbol dependencies cross object files.

Test signals: Full driver link, HDCP symbol resolution, and build variants with HDCP enabled.
