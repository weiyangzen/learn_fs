# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_mode_vba_314.h

Purpose: declares the public DCN 3.14 Display Mode Library VBA entry points used to recalculate mode support, run full mode/system configuration, and calculate writeback DISPCLK requirements. This header is the small ABI surface for the spreadsheet-derived DCN314 VBA implementation.

Important APIs/types/functions: exports `dml314_recalculate(struct display_mode_lib *mode_lib)`, `dml314_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`, and `dml314_CalculateWriteBackDISPCLK(...)`. The function signatures depend on `struct display_mode_lib` and `enum source_format_class`, which are defined by the surrounding DML headers included by users of this header.

Control flow: the header itself has no executable control flow. Consumers call `dml314_ModeSupportAndSystemConfigurationFull` to populate mode-support and system-configuration VBA state, `dml314_recalculate` to recompute after parameter changes, and `dml314_CalculateWriteBackDISPCLK` as a helper for writeback scaling and line-buffer constraints.

State and persistence: no state is stored in this header. All persistent calculation state is owned by the caller-provided `display_mode_lib` instance. The writeback helper returns a `double` and does not expose mutable state in the signature.

Dependencies and integration: guarded by `__DML314_DISPLAY_MODE_VBA_H__` and intended to be paired with the DCN314 DML implementation and common `display_mode_lib`/VBA structures. It integrates with resource validation code through function tables that select generation-specific DML callbacks.

Risks: the header forward-declares through parameter usage rather than including all defining headers, so compilation order must ensure `struct display_mode_lib` and `enum source_format_class` are visible where needed. Any signature drift from the implementation or function-table assignments would break DCN314 validation.

Test signals: compile coverage for AMD display DML is the primary signal. Runtime confidence comes from modeset/bandwidth validation paths that exercise DCN314 mode support, recalculation, and writeback clock calculations under scaled writeback formats.
