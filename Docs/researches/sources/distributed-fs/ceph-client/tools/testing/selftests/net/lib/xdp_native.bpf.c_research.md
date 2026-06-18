# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_native.bpf.c

## Purpose
This BPF object provides configurable native XDP behavior for selftests: pass, drop, transmit back, adjust tail, and adjust head for selected UDP traffic over IPv4 or IPv6.

## Important APIs and Maps
`map_xdp_setup` configures mode, UDP port, adjustment offset, and fill tag. `map_xdp_stats` counts RX, pass, drop, TX, and abort events. `xdp_prog` and `xdp_prog_frags` call `xdp_prog_common`. Major helpers include `filter_udphdr`, `record_stats`, `xdp_mode_pass`, `xdp_mode_drop_handler`, `xdp_mode_tx_handler`, `update_pkt`, `xdp_adjst_tail`, `xdp_adjst_tail_shrnk_data`, `xdp_adjst_tail_grow_data`, `xdp_head_adjst`, `xdp_adjst_head_shrnk_data`, and `xdp_adjst_head_grow_data`.

## Control Flow and State
For each packet, `xdp_prog_common` reads mode and port from `map_xdp_setup`. Pass/drop modes only count matching UDP packets. TX mode swaps MAC and IP addresses and returns `XDP_TX`. Tail/head adjustment modes update IP/UDP lengths, adjust checksums, add or remove bytes, and either pass or abort on validation/helper failure. State is held in BPF maps and packet mutations; no userspace files are written.

## Dependencies and Integration
It depends on XDP helpers and kfuncs such as weak `bpf_xdp_pull_data`, `bpf_xdp_get_buff_len`, `bpf_xdp_load_bytes`, `bpf_xdp_store_bytes`, `bpf_xdp_adjust_tail`, `bpf_xdp_adjust_head`, `bpf_csum_diff`, and atomic map increments. Userspace tests configure maps and inspect stats via bpftool.

## Risks and Test Signals
Packet mutation is bounds-sensitive and supports only UDP directly under IPv4/IPv6. IPv4 header checksum updates are incomplete for some adjustment paths compared with UDP checksum handling, so tests must know expected behavior. Invalid adjustment sizes cause `XDP_ABORTED` and increment abort stats. Pass signals are expected map counters, reflected packets for TX mode, and payload/tag/length changes observed by test traffic.
