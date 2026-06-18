# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/trx.c

Purpose: Implements RTL8192DU USB TX descriptor construction, simple aggregation handling, endpoint mapping, and mac80211 queue-to-hardware queue mapping.

Important APIs/functions: `rtl92du_tx_fill_desc()` prepends and fills the Realtek TX descriptor with packet size, rate, aggregation, RTS/CTS, bandwidth, security, queue, fallback, QoS/RDG, MAC ID, LPS sequence, BMC/more-fragment, ownership, segment bits, and checksum. `rtl92du_tx_aggregate_hdl()` dequeues a single skb. `rtl92du_endpoint_mapping()` configures USB endpoint maps. `rtl92du_mq_to_hwq()` maps beacon, management, and AC queues. Cleanup/post-URB hooks are no-op/success.

Control flow: TX descriptor fill calls `rtl_get_tcb_desc()`, reserves descriptor space with `skb_push()`, clamps 5 GHz CCK rates to OFDM, derives AMPDU state from station TID data, applies TX info flags, encodes cipher type, queue selector, rate-control fields, QoS/RDG, and power-save descriptor behavior, then computes checksum. Endpoint mapping reads MAC-specific USB queue-select registers, overrides by detected out-pipe count, and maps queues to one/two/three endpoints.

State and persistence: Mutates skb descriptor bytes and endpoint map fields in `rtl_usb`; reads live HAL/MAC/PSC/station aggregation state. No disk persistence.

Dependencies/integration: mac80211 TX metadata, rtlwifi USB/base helpers, rtl8192d descriptor setters from `trx_common.h`, local helpers from `trx.h`, and `sw.c` HAL/USB registration.

Risks: Descriptor bitfields are hardware-sensitive. skb headroom must be sufficient. Checksum must follow all descriptor writes. Endpoint detection affects queue routing. Invalid mac80211 queues default to BE with a warning.

Test signals: 2.4/5 GHz data TX, AMPDU, encrypted traffic, management/beacon TX, power-save null frames, one/two/three endpoint devices, and invalid queue/endpoint warnings.
