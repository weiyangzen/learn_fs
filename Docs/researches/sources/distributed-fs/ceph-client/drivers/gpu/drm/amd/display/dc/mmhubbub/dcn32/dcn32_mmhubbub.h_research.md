# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn32/dcn32_mmhubbub.h

Purpose: provides DCN3.2 MMHUBBUB register and mask/shift macro lists plus constructor declaration.

Important APIs/types: `MCIF_WB_COMMON_REG_LIST_DCN32` maps MCIF and MMHUBBUB registers using `SRI2`, including warmup registers. `MCIF_WB_COMMON_MASK_SH_LIST_DCN32` lists fields for buffer manager, watermarks, QoS, security, resolution, and warmup control. Exports `dcn32_mmhubbub_construct`.

Control flow/integration: resource code uses these macros to build typed register structures compatible with `struct dcn30_mmhubbub`, then constructor installs DCN32 function table.

State/persistence: header declares register metadata only. Runtime state lives in the `dcn30_mmhubbub` instance and hardware registers.

Dependencies: includes DCN20 and DCN30 MMHUBBUB headers to reuse base types and field lists.

Risks: DCN32 has a different register namespace for some watermarks and warmup fields; incorrect macro mapping can silently program wrong addresses.

Test signals: build coverage for DCN32 resource creation, warmup field programming, and writeback register access smoke tests.
