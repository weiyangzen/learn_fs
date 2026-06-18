# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.5.c

Purpose: Defines `ipa_data_v5_5`, the descriptor for IPA v5.5. It describes endpoint/channel mappings, resource groups, expanded memory layout, QSB settings, and power/interconnect votes.

Important data: Endpoint topology matches v5.0 for the main AP channels: command TX channel 12 endpoint 14, LAN RX channel 13 endpoint 16, modem TX channel 11 endpoint 2, and modem RX channel 1 endpoint 23. AP modem TX uses TLV count 25. Modem route count is 11. Memory is v5-style with UC event ring at offset 0, UC shared/info, expanded route table sizes, headers, large modem proc context, quota/tethering/filter-route/drop stats, AP v4/v6 filter regions, modem memory, NAT table, and PDN config. The descriptor has IMEM fallback 0x14688000/0x2000, SMEM 0xb000, and 120 MHz core clock.

Control flow and integration: Common IPA/GSI init uses these constants to allocate channel rings, command pools, endpoint maps, and IPA-local memory. v5.5 uses the same `gsi_regs_v5_0` register layout as v5.0/v5.2 in this driver. Immediate commands encode endpoint IDs with full 8-bit width.

State and persistence: The file is immutable descriptor data only. Programmed GSI channels, event rings, route/filter tables, and IPA memory are the resulting runtime state.

Dependencies: Depends on v5 register layouts, endpoint/memory/resource enums, DT interconnect and memory bindings, and firmware expectations for IPA-local memory offsets.

Risks: Similarity with v5.0 can hide subtle differences: IMEM size is smaller, SMEM is larger, route table sizes differ, and memory stats/AP filter regions differ. Copying v5.0 assumptions into v5.5 can corrupt modem-visible local memory or under-size fallback memory.

Test signals: v5.5 probe should pass GSI channel/event discovery, command-channel setup, and memory validation. Traffic tests should cover AP modem TX/RX and LAN RX; command tests should cover table init, pipeline clear, and DMA shared-memory commands. Modem SSR should not leave stale channel state.
