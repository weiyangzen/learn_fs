# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.h

Purpose: public header for the DCE8 hardware sequencer shim. It exposes the single constructor needed by DCE8 display initialization.

Important APIs, types, and functions: declares `dce80_hw_sequencer_construct(struct dc *dc)`, includes `core_types.h` and `hw_sequencer_private.h`, and forward-declares `struct dc`.

Control flow: no executable flow exists. Callers use the constructor to install DCE110 base functions plus DCE8-specific overrides.

State and persistence: no state is held in the header. The implementation mutates HWSS function tables and later inherited/overridden hooks program hardware state.

Dependencies and integration points: tied to DCE8 resource construction and the shared DCE110/DCE100 HWSS contracts.

Risks and test signals: risk is limited to build integration and constructor selection. Test signals are successful DCE8 compile coverage and runtime hook-table verification through mode-set and bandwidth paths.
