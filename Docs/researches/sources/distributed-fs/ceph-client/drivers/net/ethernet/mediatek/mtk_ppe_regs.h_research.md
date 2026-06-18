<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_regs.h

## Purpose
`mtk_ppe_regs.h` is the register map for the PPE block. It provides offsets and bitfields used by `mtk_ppe.c` to configure global enable, supported flow types, protocol checking, FOE table location and aging policy, bind limits/rates, VLAN MTU enforcement, cache control, MIB accounting, and secondary bus controls.

## Important Constants
Core registers include `MTK_PPE_GLO_CFG`, `MTK_PPE_FLOW_CFG`, `MTK_PPE_IP_PROTO_CHK`, `MTK_PPE_TB_CFG`, `MTK_PPE_TB_BASE`, `MTK_PPE_BIND_RATE`, `MTK_PPE_BIND_LIMIT0/1`, `MTK_PPE_KEEPALIVE`, `MTK_PPE_UNBIND_AGE`, `MTK_PPE_BIND_AGE0/1`, `MTK_PPE_DEFAULT_CPU_PORT`, `MTK_PPE_VLAN_MTU0/1`, `MTK_PPE_CACHE_CTL`, `MTK_PPE_MIB_CFG`, `MTK_PPE_MIB_TB_BASE`, `MTK_PPE_MIB_SER_*`, `MTK_PPE_MIB_CACHE_CTL`, and `MTK_PPE_SBW_CTRL`. Enums describe scan modes, keepalive modes, and search-miss behavior.

## Control Flow
The PPE implementation uses these definitions in a predictable sequence: initialize FOE table base and table config, enable protocol and flow classes, configure unbind/bind aging and bind limits, enable cache, enable global PPE execution, set CPU ports, and optionally configure MIB table base and read-clear behavior. Stop/reset paths clear aging, cache, and global enable bits and poll `MTK_PPE_GLO_CFG_BUSY`. Accounting reads write an index to `MTK_PPE_MIB_SER_CR` and read serialized counter registers after `ST` clears.

## State And Persistence
Every macro maps to live hardware register state. These registers persist until reset or reprogramming. They influence how hardware interprets the coherent FOE table, whether new flows are built on search miss, which packet types are eligible, how old entries age, how MTU drops work, and whether MIB counters are populated.

## Dependencies And Integration Points
The header depends on kernel `BIT`, `GENMASK`, and field-prep usage via including files. It is consumed by `mtk_ppe.c` and indirectly by debug/diagnostic code. It must match `mtk_ppe.h` FOE layouts and `mtk_eth_soc.h` SoC metadata such as entry size and version.

## Risks
The most visible typo-like risk is `MTK_PPE_GLO_CFG_MCAST_ENTRIES` using `GNEMASK`, which would fail compilation if referenced. Register aliases are repeated for `MTK_PPE_KEEPALIVE`, so edits should avoid divergent definitions. Incorrect masks can silently misprogram hardware, leading to dropped traffic, failure to bind flows, broken aging, or invalid accounting. MIB cache enable uses a neighboring register and must not be confused with `MTK_PPE_MIB_CFG` bits.

## Test Signals
Compilation with all warnings catches unused broken macros only if referenced. Runtime signals include PPE start reaching not-busy, FOE table used count changing, flow classes binding for IPv4/IPv6/tunnel cases, MTU drop behavior matching configured interface MTU, and MIB counters returning sane deltas under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_regs.h -->
