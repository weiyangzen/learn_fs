# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.5.c

Purpose: Defines `ipa_data_v4_5`, a v4.5 platform descriptor containing endpoint topology, resource limits, IPA-local memory map, QSB settings, and power/interconnect data.

Important data: AP command TX is channel 9 endpoint 7, AP LAN RX channel 10 endpoint 16, AP modem TX channel 7 endpoint 2, and AP modem RX channel 1 endpoint 14. Modem AP and DL NLO endpoint entries are included for table setup. AP modem TX uses 512 TRE/event entries and TLV count 16; command TX uses TLV count 20. Memory layout includes hash and non-hash filter/route regions, header areas, larger modem proc context, NAT and stats regions, modem memory, UC event ring, and PDN config. `ipa_data_v4_5` uses a 150 MHz core clock comment-marked as uncertain in source.

Control flow and integration: Consumers treat this file as authoritative configuration. `gsi_channel_init_one()` validates the AP endpoint ring sizes and allocates rings based on these values. IPA memory setup and immediate-command validation use the offsets and sizes for filter/route/header initialization. Resource data is programmed into IPA resource-management registers during config.

State and persistence: No file-local mutable state exists. These constants shape runtime `struct ipa` memory descriptors, endpoint maps, and GSI channel state, and they persist only as programmed hardware state during the driver lifetime.

Dependencies: Uses `ipa_data.h`, `ipa_endpoint.h`, `ipa_mem.h`, `ipa_power.h`, and resource definitions. IPA v4.5 selects the v4.5 GSI register descriptions, including split channel protocol encoding and prefetch-mode fields.

Risks: v4.5 differs from v4.2 in endpoint numbering, nonzero hash table regions, larger SMEM, and GSI register fields. Copying values across versions can break endpoint routing or memory canaries. The core clock uncertainty comment is a signal that power/performance regressions should be checked on hardware.

Test signals: Successful probe, no GSI validation errors, table init with hashed route/filter regions, modem data path throughput, and power/interconnect vote sanity. Watch for DMA command failures to the NAT/stats areas and for unexpected endpoint status after modem SSR.
