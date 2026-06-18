# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn21/dcn21_hubbub.h

Purpose: Declares DCN2.1 hubbub host-VM register lists, masks, constructor, and watermark helpers.

Important APIs and types: `HUBBUB_HVM_REG_LIST` adds fractional urgency bandwidth, trip-to-memory, host VM control, DCHVM memory/clock/rIOMMU registers. `HUBBUB_MASK_SH_LIST_HVM` maps VM-row watermark and host VM fields. `HUBBUB_REG_LIST_DCN21` and `HUBBUB_MASK_SH_LIST_DCN21` combine DCN20 common registers, SR watermarks, HVM, VM fault fields, and refdiv. Prototypes expose DCHVM init, DCHUB init, watermark helpers/readback, and constructor.

Control flow: resource code expands macros into DCN21 register tables and calls `hubbub21_construct`. Runtime uses the installed vtable or helper calls from DCN30.

State and persistence: no new struct; DCN21 reuses `dcn20_hubbub` and base `hubbub` state while defining extra hardware metadata.

Dependencies and integration: includes DCN20 hubbub. Integrated by DCN21 and reused by DCN30 watermark programming.

Risks and test signals: field-list/mask mismatch can silently program wrong VM-row watermark fields. Compile-time generated table checks and hardware readback after programming are important.
