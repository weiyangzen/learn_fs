# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn20/dcn20_hubbub.c

Purpose: Implements DCN2 hubbub extensions: VMID/page-table initialization, 48-bit system aperture programming, expanded DCC support, DCHUB reference-clock validation, watermarks with DCN2 request limits, and diagnostic readback.

Important APIs and functions: `hubbub2_init_dchub_sys_ctx` programs FB/AGP aperture and protection-fault default page, then initializes VMID0 when GART is present. `hubbub2_init_vm_ctx` configures per-VMID page tables. `hubbub2_update_dchub` updates ZFB/mixed/local apertures. `hubbub2_get_dcc_compression_cap` extends DCC to more formats and render swizzles. `hubbub2_get_dchub_ref_freq` validates global timer ref frequency. `hubbub2_program_watermarks` reuses DCN1 watermark helpers with pstate special-case lowering. `hubbub2_read_state` captures VM fault and debug state.

Control flow: `hubbub2_construct` installs the DCN2 function table. Initialization flows program physical aperture first, optionally VMID0, and return VMID capacity. Watermark programming follows DCN1 safe-lowering rules but adjusts outstanding request thresholds to DCN2 values.

State and persistence: `dcn20_hubbub` caches watermarks, detile buffer size, VMID objects, and generation tuning. Hardware state includes VM aperture/page tables, DCC capability-dependent programming, arbiter watermarks, fault status, and global timer state.

Dependencies and integration: depends on `dcn20_vmid`, `clk_mgr`, DC debug config, and common DCN1 hubbub helpers. Integrated by DCN2 resource pools and reused by DCN201/DCN21/DCN30.

Risks and test signals: `hubbub2_read_state` appears to assign LSB fault address into `vm_fault_addr_msb`, likely a typo. Reference clock outside 40-60 MHz asserts critically. Tests should cover VMID depth/block conversions, aperture programming for each framebuffer mode, DCC render swizzle exceptions, pstate support transitions, and VM fault readback.
