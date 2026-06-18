# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.h

Purpose: defines the DCN315-specific DMUB field macro list and declares the DCN315 register table.

Important APIs and control flow: `DMUB_DCN315_FIELDS()` mirrors `DMUB_DCN31_FIELDS()` except for GPINT interrupt enable/ack field names, using `DMCUB_GPINT2_INT_EN` and `DMCUB_GPINT2_INT_ACK`. It exports `dmub_srv_dcn315_regs` as a DCN31-compatible register table.

State and persistence behavior: no direct state. The macro list controls which bit masks/shifts are loaded into the static register descriptor used by runtime register helpers.

Dependencies and integration points: includes `dmub_dcn31.h` and is consumed by `dmub_dcn315.c`. `dmub_srv.c` depends on the exported table when selecting DCN315.

Risks and test signals: risks include incomplete field parity with DCN31, field-name divergence across generated headers, and shared functions assuming fields not present in `DMUB_DCN315_FIELDS()`. Test signals are compile-time macro expansion and GPINT interrupt handling on DCN315 hardware.
