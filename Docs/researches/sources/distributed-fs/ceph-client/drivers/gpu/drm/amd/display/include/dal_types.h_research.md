# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dal_types.h

Purpose: declares common DAL forward types and the display engine/DCN version enumeration.

Important APIs and control flow: forward-declares `dal_logger` and `dc_bios`. `enum dce_version` lists DCE 6.0 through 12.1, then DCN 1.0 through 4.2, with separate `DCE_VERSION_MAX` and `DCN_VERSION_MAX` markers.

State and persistence behavior: no state. The enum values are used as selectors for BIOS parser creation, resource construction, and version-gated display behavior.

Dependencies and integration points: includes `signal_types.h`; consumed by display core, BIOS parser, and ASIC resource code.

Risks and test signals: risks include enum ordering assumptions, max marker placement, new DCN versions needing coordinated additions, and mixed DCE/DCN comparisons. Test signals include version switch coverage for DCN 3.14/3.15/3.16/3.5/3.51/3.6/4.01/4.2 and BIOS parser/resource selection using the expected version.
