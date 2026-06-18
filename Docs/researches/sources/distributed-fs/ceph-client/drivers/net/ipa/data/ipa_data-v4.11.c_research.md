# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.11.c

Purpose: Defines `ipa_data_v4_11`, the complete boot-time descriptor for IPA v4.11 platforms. It captures the IPA/GSI topology expected by the common driver: QSB parameters, AP and modem endpoint mappings, resource groups, local memory regions, legacy IMEM/SMEM fallback values, and power/interconnect requirements.

Important data: The endpoint array maps AP command TX to channel 5 endpoint 7, AP LAN RX to channel 14 endpoint 9, AP modem TX to channel 2 endpoint 2, and AP modem RX to channel 7 endpoint 16, with modem AP and DL NLO entries present for filter/routing setup. AP rings generally use 256 entries, while AP modem TX uses a 512-entry ring and TLV count 16. The memory table includes hashed/non-hashed IPv4/IPv6 filter and route regions, modem/AP header regions, proc contexts, NAT table, PDN config, stats regions, modem memory, and an end marker. `ipa_data_v4_11` sets `modem_route_count = 8` and a 60 MHz core clock.

Control flow and integration: The descriptor is selected by Device Tree match data and passed through IPA initialization. `gsi_init()` uses AP endpoint entries to allocate rings, command DMA pools, and NAPI contexts. `gsi_setup()` later validates hardware channel/event counts and programs GSI context registers. IPA table and command initialization validate the memory regions supplied here before issuing immediate commands.

State and persistence: All objects here are `static const` or exported `const`, so the file has no mutable state. Runtime state appears after consumers copy or reference these constants into `struct ipa` and program registers and IPA SRAM.

Dependencies: Depends on `ipa_data.h`, endpoint/memory enums, resource constants, and interconnect names matching platform DT. It also interacts indirectly with `gsi_reg.c`, because IPA v4.11 selects the v4.11 GSI register definition set and uses generic-command parameters for flow-control behavior.

Risks: v4.11 has version-sensitive register behavior: GSI generic commands include `GENERIC_PARAMS`, and channel/event register fields differ from v5.0. Incorrectly reusing v5.x endpoint IDs or memory offsets would break table initialization. The local memory table contains canary-protected regions, so offset/size drift can surface as memory validation failures or modem crashes.

Test signals: Probe on v4.11 DT should complete without GSI channel-not-supported errors. IPA command init should validate header and register-write offsets. Runtime tests should include modem channel flow-control toggles, AP command TX immediate commands, NAT/stats memory access, and suspend/resume channel stop/start.
