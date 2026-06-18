# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.0.c

Purpose: Defines `ipa_data_v5_0`, the first v5.x descriptor in this set. It describes the v5.0 endpoint topology, resource limits, reordered local memory layout, QSB parameters, and power/interconnect requirements.

Important data: AP command TX is channel 12 endpoint 14, AP LAN RX channel 13 endpoint 16, AP modem TX channel 11 endpoint 2, and AP modem RX channel 1 endpoint 23. AP modem TX has TLV count 25, higher than older versions. Modem route count rises to 11. Local memory starts with `IPA_MEM_UC_EVENT_RING` at offset 0, then UC shared/info, table regions, headers, proc contexts, stats, AP filter regions, modem memory, NAT table, and PDN config. The descriptor provides legacy IMEM fallback 0x14688000/0x3000 and SMEM 0x9000, with 120 MHz core clock.

Control flow and integration: IPA v5.0 selects `gsi_regs_v5_0`. In `gsi_channel_program()`, v5.0 moves event ring index from `CH_C_CNTXT_0` to `CH_C_CNTXT_1`, uses v5 hardware event count discovery, keeps `DB_IN_BYTES`, and supports wider endpoint IDs in immediate commands. `ipa_cmd_ip_packet_init_add()` writes the full endpoint byte on v5+.

State and persistence: Static descriptor only. Runtime state is built by GSI ring allocation, IPA memory setup, resource programming, and table initialization.

Dependencies: Depends on v5.0 register descriptions, endpoint IDs up to 23, memory IDs including AP-specific filter regions, and resource limits matching hardware/firmware. Interconnect names must match DT for power setup.

Risks: v5.0 has major layout changes from v4.x: endpoint IDs are wider, memory starts with UC event ring, route entries are larger, and GSI event count discovery uses `HW_PARAM_4`. Backporting v4 assumptions can break command payload encoding or channel programming.

Test signals: Probe should report correct hardware channel/event counts via `HW_PARAM_2`/`HW_PARAM_4`; AP command pipeline clear should route through full 8-bit endpoint IDs; modem route count 11 should size route tables correctly; data path should exercise larger AP modem TX TLV depth.
