<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/lnl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/lnl.c

Purpose: Lunar Lake/Future Core link-interrupt routing adjustment layered on Meteor Lake core stall behavior.

Important APIs, types, and functions: `avs_lnl_core_stall()`.

Control flow: calls `avs_mtl_core_stall()` for the actual core stall/unstall operation. After successful unstall, iterates HDA extended links and sets `AZX_ML_LCTL_OFLEN` so link interrupts are routed to DSP firmware.

State and persistence: modifies ML link control registers after unstall; no file-local state.

Dependencies and integration points: depends on MTL core stall implementation, HDA extended bus link list, and register definitions. Used indirectly by platform ops for LNL/PTL-style descriptors.

Risks: if hlink list is incomplete or link register writes fail silently, firmware may miss offload link interrupts. Behavior only runs on unstall, so later link additions would need separate routing.

Test signals: after DSP unstall, each multi-link control register has OFLEN set and firmware receives link interrupts on LNL-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/lnl.c -->
