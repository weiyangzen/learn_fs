# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.h

Purpose: minimal public header for the DCE11.2 hardware sequencer shim. It exposes only the constructor needed by DCE11.2 display resource initialization.

Important APIs, types, and functions: declares `dce112_hw_sequencer_construct(struct dc *dc)`. It includes `core_types.h` and `hw_sequencer_private.h`, and forward-declares `struct dc`.

Control flow: no executable flow exists in the header. Users include it and call the constructor, which installs the DCE110 base table and then overrides display power-gating behavior.

State and persistence: no direct state. The constructor signature passes the global display core object whose HWSS function tables will be mutated by the implementation.

Dependencies and integration points: integrated with DCE11.2 resource construction and indirectly with the DCE110 HWSS contract. The include guard isolates this generation-specific interface.

Risks and test signals: risk is limited to build integration and selecting the correct constructor for DCE11.2 ASIC paths. Test signals are successful compilation and runtime confirmation that `enable_display_power_gating` resolves to the DCE112 override.
