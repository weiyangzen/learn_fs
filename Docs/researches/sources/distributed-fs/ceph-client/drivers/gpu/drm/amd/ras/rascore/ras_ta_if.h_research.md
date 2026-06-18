# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_ta_if.h

Purpose: this header defines the host-side ABI for commands exchanged with the RAS Trusted Application through PSP shared memory.

Important definitions: `RAS_TA_HOST_IF_VER` is the host interface version. `enum ras_ta_cmd_id` covers feature enable/disable, trigger-error, block/subblock queries, and address queries. `enum ras_ta_status` enumerates success and TA/TEE/RAS error statuses. `enum ras_ta_block`, `ras_ta_mca_block`, `ras_ta_error_type`, `ras_ta_address_type`, and `ras_ta_nps_mode` define command domains. Input/output structs include feature toggles, trigger-error fields, TA init flags, MCA and physical address descriptors, query-address input/output, and output flags. `union ras_ta_cmd_input`, `union ras_ta_cmd_output`, and `struct ras_ta_cmd` form the shared command buffer layout.

Control flow and state: no code exists here. The packed-ish ABI is interpreted by `ras_psp.c` and TA firmware. Persistence is not represented.

Dependencies and integration: PSP transport writes `struct ras_ta_cmd` into GPU memory and checks `if_version`, `ras_status`, and output flags. UMC uses query-address for MCA-to-PA translation when supported. GFX/SDMA/VCN/JPEG injection uses trigger-error. Risks include ABI drift with TA firmware, enum value stability, command union size assumptions, and misspelled/uppercase constants that still affect source compatibility. Test signals should include shared-buffer size checks, interface-version rejection, each status-code diagnostic path, trigger-error instance packing, and query-address round trips.
