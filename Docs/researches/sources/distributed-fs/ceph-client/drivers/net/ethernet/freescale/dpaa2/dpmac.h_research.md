# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac.h

Purpose: Public in-driver DPMAC API declaration header. It defines DPMAC link/interface enums, link options, advertised speeds, attributes, link-state configuration, counter IDs, and prototypes for the command wrappers in `dpmac.c`.

Important APIs, types, and functions: Core types include `enum dpmac_link_type`, `enum dpmac_eth_if`, `struct dpmac_attr`, `struct dpmac_link_state`, and `enum dpmac_counter_id`. Link option macros cover autonegotiation, half duplex, pause, and asymmetric pause. Advertised-speed masks cover common 10/100/1000/2500/10000 full-duplex and autoneg. Prototypes expose open/close, attribute read, link-state set, counter read, API version, protocol set, and bulk statistics.

Control flow: No direct flow. Callers open a DPMAC object to get a token, read attributes to learn link type/interface/rate, push link state as PHY/phylink changes, query counters/statistics, optionally change MAC protocol, and close the token when done.

State and persistence behavior: The header declares transient request/response structs and enum IDs. Link configuration/state is persisted only in MC/DPMAC hardware. Counter IDs describe hardware-maintained counters; reads are snapshots.

Dependencies and integration points: Forward-declares `struct fsl_mc_io` and is included by DPMAC wrapper code and higher-level DPAA2 MAC/switch code. It is part of the internal contract between DPMAC MC objects and netdev/phylink integration.

Risks: `enum dpmac_counter_id` numeric order is a firmware ABI used in single and bulk statistics commands; reordering breaks counter reads. Link and advertised option bit positions must match MC firmware. `struct dpmac_link_state` uses `int` for boolean-like fields but command packing stores one-bit values; callers should pass normalized 0/1 values. Comment typos do not affect ABI but can obscure counter semantics.

Test signals: Build coverage for all users, phylink mode mapping for each `dpmac_eth_if`, fixed/PHY/backplane link types, link option translation, all counter IDs including PFC counters, bulk statistics counter-list construction, and unsupported protocol/link combinations from firmware.
