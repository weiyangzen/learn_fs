# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.9.c

Purpose: Provides `ipa_data_v4_9`, a v4.9 hardware descriptor with GSI endpoint topology, IPA memory layout, resource allocation limits, QSB parameters, and power/interconnect votes.

Important data: AP command TX uses channel 6 endpoint 7, AP LAN RX channel 7 endpoint 11, AP modem TX channel 2 endpoint 2, and AP modem RX channel 12 endpoint 20. Modem AP RX shares channel 7 but is modem-owned and not initialized as an AP channel. Memory includes the full hashed/non-hashed table set, modem/AP headers, large modem proc context, NAT table, quota/tethering/filter-route/drop stats, modem memory, UC event ring, and PDN config. The descriptor sets `version = IPA_VERSION_4_9`, `modem_route_count = 8`, SMEM 0x9000, and 60 MHz core clock.

Control flow and integration: IPA v4.9 selects `gsi_regs_v4_9`. GSI channel programming enables `DB_IN_BYTES` for v4.9+, so this descriptor's channels are paired with byte-addressed doorbell behavior in `gsi_channel_program()`. IPA command code validates table and header regions and allocates command payloads from the AP command channel defined here.

State and persistence: All tables are immutable. Runtime state appears in GSI rings, NAPI contexts, endpoint maps, IPA memory, and modem route/filter tables configured from these constants.

Dependencies: Depends on endpoint/memory/resource enum stability and on DT interconnect names matching `memory`, `imem`, and `config` style entries used by the power layer. Also depends on v4.9 register descriptors for DB-in-bytes fields.

Risks: v4.9 channel IDs differ from v4.7/v4.11 even where endpoint names are similar. The DB-in-bytes register behavior makes GSI ring programming version-sensitive. Mistyped stats or NAT offsets can corrupt modem-visible memory while probe still succeeds.

Test signals: Hardware probe without unsupported-channel messages, successful route/filter table initialization, BQL accounting on TX completions, and modem SSR recovery. Watch for GSI event-with-no-transaction warnings, table command failures, and unexpected general interrupts.
