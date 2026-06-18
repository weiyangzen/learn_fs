# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/dr.c

## Purpose
`dr.c` defines MAC/base configuration and firmware declaration for DR-family devices introduced in 2024-2025, using core max 102/API min 100, EHT queue sizing, DBGC/DBGI monitor registers, Gen2 integrated transport, and the `iwlwifi-dr-a0-pe-a0` firmware prefix.

## Important APIs, Types, and Data
- Firmware prefix/core: `IWL_DR_A_PE_A_FW_PRE`, `IWL_DR_UCODE_CORE_MAX`, `IWL_DR_UCODE_API_MIN`.
- `iwl_dr_base`: 512 queues, 65536 max TFD queue size, min TXQ 128, EHT BA queue size, SMEM, checksum features, MAC address CSR offset 0x30, D3 debug data, GP2 address, SMEM/DRAM/DBGI monitor registers.
- `iwl_dr_mac_cfg`: device family DR, Gen2, integrated, MQ RX, UMAC PRPH offset, long low-latency xtal, LTR delay.
- `IWL_CORE_FW` declares the firmware image for the core release.

## Control Flow and Integration
MLD/PCI matching selects `iwl_dr_mac_cfg` with a PE RF config. Transport uses the base queue and monitor definitions, and firmware loader sees the `IWL_CORE_FW` alias.

## State and Persistence Behavior
Immutable config only. Runtime queue, debug, monitor, and latency state is derived from this data.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-prph.h`, and `fw/api/txq.h`. The top-level Makefile includes it for `CONFIG_IWLMLD`.

## Risks and Edge Cases
DR is newer and tightly tied to EHT queue sizing and core firmware versioning. Misaligned firmware prefix/core, MAC family, or RF pairing can prevent probe or produce unsupported capability exposure.

## Test Signals
Build MLD, validate firmware alias generation, probe DR hardware or PCI ID simulation, verify EHT TXQ sizing, DBGC/DBGI monitor collection, checksum offload, UMAC PRPH access, and suspend/resume with long-latency settings.
