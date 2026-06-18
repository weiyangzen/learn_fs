# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c

Purpose: instantiates the DCN 3.1.5 DMUB register table. DCN315 largely reuses DCN31 hardware behavior but uses a local field list because GPINT interrupt fields are named `DMCUB_GPINT2_INT_EN` and `DMCUB_GPINT2_INT_ACK`.

Important APIs and control flow: `dmub_srv_dcn315_regs` expands common DCN31 register offsets plus `DMUB_DCN315_FIELDS()` for masks and shifts. The file has no runtime functions beyond the table initializer; all hardware operations are inherited from DCN31 through `dmub_srv_hw_setup()`.

State and persistence behavior: the exported const register table is immutable. Runtime DMUB state remains in the DMCUB hardware registers and in `struct dmub_srv` ring-buffer counters.

Dependencies and integration points: depends on `dcn_3_1_5_offset.h`, `dcn_3_1_5_sh_mask.h`, `dmub_reg.h`, and `dmub_dcn315.h`. `dmub_srv_hw_setup()` uses the table for `DMUB_ASIC_DCN315` while assigning the common DCN31 function set.

Risks and test signals: risks include a mismatch between the DCN315-specific interrupt field names and shared GPINT dataout code, register macro drift, and segment-base errors. Test signals include build coverage, GPINT dataout interrupt disable/ack/re-enable working on DCN315, and normal DCN31 reset/window/mailbox flows using the DCN315 offsets.
