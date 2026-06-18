# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp_eth.c

Purpose: Parses and mutates the NSP Ethernet table that describes physical ports, media, speed, FEC, pause, autonegotiation, and split configuration.

Important APIs/types/functions: `union eth_table_entry` mirrors raw NSP table entries. `nfp_eth_read_ports()` and `__nfp_eth_read_ports()` build `struct nfp_eth_table`. `nfp_eth_config_start()`, `_commit_end()`, and `_cleanup_end()` stage and finalize table edits. Setters include `nfp_eth_set_mod_enable()`, `nfp_eth_set_configured()`, `nfp_eth_set_idmode()`, `nfp_eth_set_fec()`, `nfp_eth_set_pauseparam()`, and internal `__nfp_eth_set_aneg/speed/split()`.

Control flow: Reading fetches a fixed-size table, counts entries with lane bits set, validates optional returned count, allocates a flexible table, translates raw fields according to ABI minor, computes port geometry/split state, port type, and optional media link modes. Configuration reads the table, validates the target entry, records mutations in raw state/control bits, marks the NSP state modified, then writes the whole table back only if changed.

State and persistence: Parsed tables are heap snapshots. Configuration writes can alter persistent firmware/HWInfo overrides for FEC, speed, split, and autoneg as described by comments. NSP config state owns the temporary raw entries until commit/cleanup.

Dependencies/integration: Depends on NSP buffer commands, ethtool constants, NFP FEC/link-mode definitions, and CPP logging. NIC and ethtool paths consume the parsed port table and setters.

Risks: ABI-minor gates are critical; older firmware lacks reliable configured/idmode/pause/media fields. Raw bitfield mutation must preserve unrelated fields. Port index bounds are assumed by callers. The snapshot contains duplicated-looking braces/lines around one ABI check, so build validation is important.

Test signals: Read tables with zero/nonzero returned counts, ABI minor 16/22/33/37 feature matrices, split-port geometry and duplicate subport warning, every setter no-change vs modified commit path, unsupported ABI errors, invalid speed mapping, and media read failure logging.
