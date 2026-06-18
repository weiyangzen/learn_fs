# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/cfg/bz.c

## Purpose
`bz.c` defines MAC/base configuration for BZ/GL Wi-Fi 7-era devices, using core-release-based firmware API encoding, 512 queues, EHT BA queue sizing, SMEM/debug regions, DBGC/DBGI monitor registers, Gen2 transport, integrated BZ and discrete GL variants, and exported KUnit-visible config.

## Important APIs, Types, and Data
- Firmware versioning: core max 102 encoded as API max, API min 100.
- `iwl_bz_base`: 512 queues, 65536 max TFD queue size, min TXQ 128, EHT BA queue size, SMEM, checksum features, MAC address CSR offset 0x30, D3 debug data, GP2 address, SMEM/DRAM/DBGI monitor registers.
- MAC configs: `iwl_bz_mac_cfg` and `iwl_gl_mac_cfg`.
- `iwl_bz_mac_cfg` is integrated with long/low-latency xtal and LTR delay; `iwl_gl_mac_cfg` is non-integrated but otherwise Gen2 with UMAC PRPH offset.

## Control Flow and Integration
PCI tables select BZ or GL MAC config, then pair with RF configs such as FM/GF/HR. Transport setup uses base queue and monitor definitions; firmware loading uses core-as-API versioning and RF file firmware declarations.

## State and Persistence Behavior
The file is immutable configuration. Runtime state derives queue sizes, firmware debug buffers, monitor pointers, and latency behavior from the selected config.

## Dependencies and Integration Points
It depends on `iwl-config.h`, `iwl-prph.h`, and `fw/api/txq.h`. It is built for both MVM and MLD in the Makefile and exports `iwl_bz_mac_cfg` for KUnit when enabled.

## Risks and Edge Cases
BZ and GL differ in integration and latency settings; wrong matching can affect power management. Core-release version encoding must match firmware declaration macros in RF files. EHT queue sizing and DBGI monitor registers are newer paths that need firmware compatibility.

## Test Signals
Build MVM and MLD configurations, run KUnit references to exported config, probe BZ/GL devices, verify core firmware selection, EHT queue sizing, DBGC/DBGI monitor dump capture, checksum offload, and long-latency suspend/resume behavior.
