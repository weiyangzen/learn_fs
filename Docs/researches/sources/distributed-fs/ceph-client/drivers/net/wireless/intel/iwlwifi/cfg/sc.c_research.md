# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/sc.c

## Purpose
`sc.c` defines MAC/base configuration and firmware declarations for SC-family devices, using core max 102/API min 100, EHT queue sizing, SMEM/debug regions, DBGC/DBGI monitor registers, Gen2 integrated transport, long low-latency xtal settings, and multiple FM/WH firmware prefixes.

## Important APIs, Types, and Data
- Firmware prefixes: SC FM B/C, SC WH A, SC2 FM C, SC2 WH A.
- `iwl_sc_base`: 512 queues, 65536 max TFD queue size, min TXQ 128, EHT BA queue size, SMEM, checksum features, MAC address CSR offset 0x30, D3 debug data, GP2 register, SMEM/DRAM/DBGI monitor registers, API range.
- `iwl_sc_mac_cfg`: device family SC, integrated, Gen2, MQ RX, UMAC PRPH offset, xtal latency 12000, low latency xtal, LTR delay.
- `IWL_CORE_FW` declarations for all SC/SC2 prefixes.

## Control Flow and Integration
MLD or MVM paths pair SC MAC config with RF configs such as FM/GF/HR/WH. Transport setup uses the base queue and monitor definitions; firmware loader uses the core firmware aliases.

## State and Persistence Behavior
Immutable config only. Runtime queue allocation, monitor state, checksum offload, firmware debug, and latency programming derive from these constants.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-prph.h`, and `fw/api/txq.h`. The Makefile includes it for both `CONFIG_IWLMVM` and `CONFIG_IWLMLD`.

## Risks and Edge Cases
SC and SC2 firmware prefixes must remain aligned with RF pairings and core release. EHT BA queue sizing and DBGI monitor registers require matching firmware support. Shared inclusion by MVM and MLD requires symbol uniqueness and config compatibility.

## Test Signals
Build MVM and MLD, verify firmware aliases, probe SC/SC2 IDs, validate EHT queue sizing, DBGC/DBGI monitor dump collection, checksum offload, UMAC PRPH access, and long-latency suspend/resume.
