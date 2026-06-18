# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vcap.c

Purpose: implements the generic Microsemi/Microchip Ocelot VCAP programming layer for IS1, IS2, and ES0 TCAM blocks. It converts `struct ocelot_vcap_filter` objects into packed key/action/counter cache words, mirrors software rule order into hardware TCAM rows, initializes VCAP memories, and manages IS2 auxiliary resources such as policers and mirror sessions.

Important APIs and types: internal `struct vcap_data` holds cache-format entry, mask, action, counter, type-group, and per-subword offsets. Exported APIs include `ocelot_vcap_init`, `ocelot_vcap_filter_add`, `ocelot_vcap_filter_del`, `ocelot_vcap_filter_replace`, `ocelot_vcap_filter_stats_update`, `ocelot_vcap_block_find_filter_by_id`, `ocelot_vcap_policer_add`, and `ocelot_vcap_policer_del`. Packing helpers include `vcap_key_set`, `vcap_key_bytes_set`, `vcap_key_bit_set`, `vcap_action_set`, and block-specific encoders `is1_entry_set`, `is2_entry_set`, and `es0_entry_set`.

Control flow: `ocelot_vcap_init` programs a discard policer, initializes rule lists, detects hardware constants from `VCAP_CONST_*`, and clears each VCAP block. Add/delete operations first update the software list sorted by priority, then rewrite affected hardware entries to preserve ordering. Adds shift lower-priority entries down, reading counters before moves; deletes remove auxiliary resources, shift following entries up, and clear the duplicated tail entry. Stats update reads the hardware counter, copies it to `filter->stats.pkts`, then rewrites the entry with a zero counter.

State and persistence: persistent runtime state is in `ocelot->block[*].rules`, `block->count`, `ocelot->vcap[*]` hardware constants, and `ocelot->vcap_pol.pol_list`. The actual hardware state is volatile TCAM/cache/counter memory and policer configuration. The policer list uses refcounts so multiple filters can share a policer index.

Dependencies and integration: depends on Ocelot core register helpers, `struct vcap_props` field maps, Linux lists/refcounts, `qos_policer_conf_set`, mirror helpers, and TC flower offload users that allocate `struct ocelot_vcap_filter`. `vsc7514_regs.c` supplies the field offsets consumed here.

Risks: bit-level packing is sensitive to field widths, type-group offsets, byte order, and action table counts. IS2 MAC_ETYPE classification has a hardware limitation: MAC_ETYPE rules for ARP/IP/SNAP-style frames cannot be mixed with non-MAC_ETYPE rules on the same port/lookup, so the code enforces exclusivity. `vcap_cmd` silently returns for out-of-range entry selections. Counter preservation during entry moves is important to avoid losing packet stats.

Test signals: exercise TC flower rules for VLAN, MAC, ARP, IPv4, IPv6, TCP/UDP ports, mirror, police/drop, replace/delete, and stats reads. Validate priority ordering, rule movement, counter clearing, policer refcount behavior, and rejection of incompatible IS2 key mixtures through extack.
