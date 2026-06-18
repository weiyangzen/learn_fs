# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_ptp.h

## Purpose
`hclge_ptp.h` defines the PF PTP register map, software PTP state, command payloads, timestamp configuration bits, and exported PTP helper prototypes. It is shared by the PF main header and PTP implementation.

## Important Types And Constants
- Register offsets under `HCLGE_PTP_REG_OFFSET` cover TX timestamp sequence/nsec/sec registers, current/set time registers, adjust/sync registers, cycle quotient/numerator/denominator registers, and masks for nsec/seconds fields.
- `HCLGE_PTP_FLAG_EN`, `HCLGE_PTP_FLAG_TX_EN`, and `HCLGE_PTP_FLAG_RX_EN` are per-PTP mode flags.
- `struct hclge_ptp_cycle` stores hardware cycle quotient, numerator, and denominator used by frequency adjustment.
- `struct hclge_ptp` stores the PTP clock, outstanding TX skb, flags, PTP MMIO base, `ptp_clock_info`, cached `kernel_hwtstamp_config`, lock, cached hardware config, last sequence id, cycle values, and diagnostic counters.
- `struct hclge_ptp_int_cmd` and `struct hclge_ptp_cfg_cmd` define firmware command payloads for interrupt enable and mode configuration.
- Enums encode supported UDP PTP packet matching modes, PTP message type modes, and PTP v2 message subtype fields.
- `hclge_ptp_get_hdev()` maps a `ptp_clock_info` callback pointer back to `struct hclge_dev`.

## Control Flow And Integration
Callers use the declared functions to initialize/uninitialize PTP, set/get hardware timestamp config, provide TX timestamp skb state, attach RX timestamps, expose ethtool timestamp info, and query hardware config for diagnostics. The header depends on Linux PTP/net timestamp headers and forward-declares `struct hclge_dev` and `struct ifreq`.

## State And Risks
The state object contains both lifecycle-owned resources (`clock`, `tx_skb`) and live hardware configuration shadow (`flags`, `ts_cfg`, `ptp_cfg`, `cycle`). Changes to masks or offsets directly affect MMIO access correctness. The TX skb pointer requires careful lifecycle cleanup during uninit/reset. `spinlock_t lock` is documented as protecting PTP registers, so new paths touching multi-register time state should use it consistently.

## Test Signals
Build coverage verifies the ABI between `hclge_main.h`, `hclge_ptp.c`, and PF op tables. Runtime signals include PHC creation, timestamp mode changes, TX/RX timestamp counters, frequency and time adjustment behavior, reset reinitialization, and debug hardware config queries.
