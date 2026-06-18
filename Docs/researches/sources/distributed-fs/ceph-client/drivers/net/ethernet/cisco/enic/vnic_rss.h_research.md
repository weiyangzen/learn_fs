# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rss.h

## Purpose
`vnic_rss.h` defines the memory layouts for Cisco ENIC RSS key and RSS CPU indirection data passed to firmware.

## Important APIs, types, and functions
- `ENIC_RSS_BYTES_PER_KEY`, `ENIC_RSS_KEYS`, and `ENIC_RSS_LEN` define a 40-byte key split across four padded key entries.
- `union vnic_rss_key` provides structured byte access and raw 64-bit access.
- `union vnic_rss_cpu` provides 32 padded CPU entries and raw 64-bit access.

## Control flow and state
The unions are filled by ENIC RSS setup code and passed as coherent DMA buffers to `CMD_RSS_KEY` and `CMD_RSS_CPU`. Firmware persists the resulting RSS state.

## Dependencies and integration points
`enic_set_rss_key()` and `enic_set_rss_cpu()` use these layouts through `vnic_dev_cmd()`. The NIC config command controls whether RSS is enabled and which hash types are used.

## Risks and test signals
Layout/padding mistakes would corrupt firmware RSS programming. Test RSS hash distribution, indirection table changes, and capability-limited hash type programming.
