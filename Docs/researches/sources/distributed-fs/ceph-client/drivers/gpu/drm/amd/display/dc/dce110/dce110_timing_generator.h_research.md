## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator.h

Purpose: shared DCE timing-generator interface and object definition. It provides sync constants, trigger-source enums, offset storage, the `dce110_timing_generator` container, and declarations reused by DCE60, DCE110 video, and DCE120 implementations.

Important types and APIs: `struct dce110_timing_generator_offsets`, `struct dce110_timing_generator`, `DCE110TG_FROM_TG`, trigger enums, `dce110_timing_generator_construct`, timing validation/programming helpers, blanking/color helpers, DRR/static-screen helpers, sync/reset helpers, CRC helpers, and `dce110_is_two_pixels_per_container`.

Integration: later ASICs reuse the base structure and many functions while swapping vtables. Offsets let one implementation address multiple CRTC/DCP instances. DCE12-specific minimum timing fields are predeclared in the base structure.

Risks and test signals: header changes have wide blast radius because multiple ASIC versions depend on this ABI. Check build coverage across DCE60/DCE80/DCE110/DCE120, and runtime coverage for all function-table entries.
