# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn20/dcn20_hubbub.h

Purpose: Declares DCN2 hubbub register lists, masks, object layout, and public helpers.

Important APIs and types: `struct dcn20_hubbub` embeds `hubbub`, register metadata, cached watermarks, 16 VMID objects, detile/CRB/compbuf sizing, pixel chunk and DET sizes, and SDPIF rate-limit policy. `HUBBUB_REG_LIST_DCN20_COMMON`, `HUBBUB_REG_LIST_DCN20`, and `HUBBUB_MASK_SH_LIST_DCN20` add VM aperture/fault/protection registers to common hubbub fields. Prototypes expose VM context setup, DCHUB init/update, DCC helpers, reference clock readout, watermark readback, and full state readback.

Control flow: generation resource code expands the macros and calls `hubbub2_construct`. Runtime interactions happen through `hubbub_funcs` or exported helpers reused by later generations.

State and persistence: cached watermarks and VMID objects are software state; hardware state is in VM, watermark, and aperture registers.

Dependencies and integration: includes DCN10 hubbub and DCN20 VMID. It is the base struct reused by DCN201, DCN21, and DCN30 constructors.

Risks and test signals: `hubbub2_initialize_vmids` is declared with a DCC-like signature but not implemented in the read file set, suggesting stale declaration risk. Build and sparse checks should catch unused or mismatched declarations; VMID count tests should validate 16-entry bounds.
