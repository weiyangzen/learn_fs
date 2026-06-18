# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/vsc7514_regs.c

Purpose: VSC7514 register and VCAP layout description used by the generic Ocelot core. It maps symbolic register IDs to target offsets, defines replicated regfields, and provides field offsets/widths for ES0, IS1, and IS2 VCAP keys/actions.

Important exports: `vsc7514_regfields`, `vsc7514_regmap`, and `vsc7514_vcap_props`. Internal tables cover ANA, QS, QSYS, REW, SYS, VCAP, PTP, DEV_GMII register targets and VCAP field tables for ES0/IS1/IS2. `vsc7514_vcap_props` associates ES0 with target S0, IS1 with S1, and IS2 with S2, including action type widths and action layout counts.

Control flow: no executable control flow beyond static initialization. Ocelot probe assigns these tables into `ocelot->map` and `ocelot->vcap`; later core helpers index into them for `regmap` access and VCAP bit packing.

State and persistence: all data is immutable after load. The tables encode a hardware ABI: offsets, bit positions, replicated register counts, and action/key widths. Hardware runtime state is not stored here.

Dependencies and integration: includes shared Ocelot VCAP and VSC7514 register definitions plus the private Ocelot header. It is consumed by `ocelot_vsc7514.c`, generic Ocelot register helpers, and `ocelot_vcap.c` packing logic.

Risks: wrong offsets or field widths create silent hardware misprogramming. The IS1 action table explicitly notes manual fields shifted by 2, so future edits must preserve driver-verified corrections rather than blindly matching datasheet text. VCAP key overlap is intentional for type-specific layouts; accidental field reuse changes can corrupt classifier behavior.

Test signals: register smoke tests on probe, TC flower rules covering ES0 VLAN tag rewrites, IS1 classification actions, IS2 ACL actions, PTP register use, MAC learning/flooding paths, and comparisons of programmed hardware behavior against expected field maps.
