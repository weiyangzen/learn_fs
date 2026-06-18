# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/ethtool.c

## Purpose
`ethtool.c` exposes ixgbevf diagnostics and tunables through `struct ethtool_ops`: driver info, register dumps, ring sizing, stats strings/data, self tests, interrupt coalescing, RSS metadata, link settings, and private flags.

## Important APIs, types, and functions
- Stats model: `struct ixgbe_stats`, `ixgbevf_gstrings_stats`, queue stats naming, and `ixgbevf_get_ethtool_stats()`.
- Register dump/test: `ixgbevf_get_regs_len()`, `ixgbevf_get_regs()`, `struct ixgbevf_reg_test`, `reg_pattern_test()`, `reg_set_and_check()`, and `ixgbevf_reg_test()`.
- Ring control: `ixgbevf_get_ringparam()` and `ixgbevf_set_ringparam()`.
- Diagnostics: `ixgbevf_diag_test()` and `ixgbevf_link_test()`.
- Coalescing and RSS: `ixgbevf_get_coalesce()`, `ixgbevf_set_coalesce()`, `ixgbevf_get_rxfh()`, key/indir-size helpers.
- Private flag: `legacy-rx` toggled through `ixgbevf_get_priv_flags()` and `ixgbevf_set_priv_flags()`.

## Control flow and integration
`ixgbevf_set_ethtool_ops()` installs a static ops table on the netdev. Ring resize validates and aligns requested descriptor counts, takes the reset bit, allocates replacement rings while the device is still running, brings the interface down, swaps resources, updates adapter counts, restarts the device, and frees temporary resources. Offline self-test closes or resets the device, performs register tests, resets again, and reopens if needed. RSS retrieval uses cached X550 VF state for newer MACs and mailbox reads under `mbx_lock` for older devices.

## State and persistence behavior
The file reads and mutates `struct ixgbevf_adapter`: message level, ring counts, ring resource contents, stats, state bits, interrupt throttle settings, RSS key/indir tables, and private flags. It also reads and writes VF MMIO registers during tests and register dumps. Changes persist for the driver lifetime and may trigger device reinitialization.

## Dependencies
It depends on Linux ethtool/netdevice/PCI/vmalloc APIs, ixgbevf ring setup/free/open/close/reset helpers, mailbox RSS helpers, MMIO accessors, u64 stats synchronization, and VF register definitions.

## Risks
- Ring resizing while running has many cleanup paths; missed frees or copied XDP RX queue state would leak resources or corrupt XDP registration.
- Offline register tests write device registers and must not run on removed hardware.
- Coalescing rejects TX settings on mixed RX/TX vectors; future vector layout changes must preserve this rule.
- Stats string count must match stats data order exactly.
- Private flag changes reset the interface and can disrupt traffic.

## Test signals
Run `ethtool -i`, `-d`, `-S`, `-g/-G`, `-c/-C`, `-t online/offline`, RSS queries, and private-flag toggles on supported VFs. Validate ring resize under running/stopped interfaces, allocation failure injection, removed-device checks, and stats string/data length consistency.
