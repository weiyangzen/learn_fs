# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce60/dce60_hwseq.h

Purpose: public header for the DCE6 hardware sequencer adaptation. It exposes the constructor used to install DCE6-specific HWSS overrides.

Important APIs, types, and functions: declares `dce60_hw_sequencer_construct(struct dc *dc)`, includes `core_types.h` and `hw_sequencer_private.h`, and forward-declares `struct dc`.

Control flow: no executable flow exists in this header. Resource construction calls the constructor, which first installs DCE110 defaults and then replaces hooks that differ on DCE6.

State and persistence: no direct state. The implementation mutates the `dc` object's HWSS/private function tables and later programs hardware state through those hooks.

Dependencies and integration points: integrated with DCE6 display resource initialization and with the DCE110/DCE100 shared HWSS interfaces. The header keeps the older generation entry point isolated from newer generation files.

Risks and test signals: risk is incorrect constructor selection or missing prototype coverage in DCE6 builds. Test signals are compile coverage and runtime confirmation that the DCE6 surface and locking overrides are active.
