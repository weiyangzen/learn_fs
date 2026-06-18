# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/ethtool.c

## Purpose
`ethtool.c` exposes the VF driver's user-facing diagnostics and tunables through `struct ethtool_ops`. It reports link settings, selected registers, statistics, ring sizes, interrupt coalescing, driver info, and a simple link self-test while rejecting unsupported operations such as EEPROM, pause, WOL, and link mode changes.

## Important APIs, Types, And Functions
The central registration function is `igbvf_set_ethtool_ops()`. Important callbacks include `igbvf_get_link_ksettings()`, `igbvf_get_regs()`, `igbvf_get_ringparam()`, `igbvf_set_ringparam()`, `igbvf_diag_test()`, `igbvf_get_coalesce()`, `igbvf_set_coalesce()`, `igbvf_get_ethtool_stats()`, `igbvf_get_strings()`, and `igbvf_nway_reset()`. `igbvf_gstrings_stats[]` maps visible stat names to adapter fields and base counters.

## Control Flow
Etthool requests enter the callback table. Ring resizing validates requested counts, clamps and aligns them, serializes against reset using `__IGBVF_RESETTING`, and if running, brings the interface down, allocates replacement resources, swaps ring structs, and brings the interface back up. Coalescing converts requested microseconds into EITR units or adaptive modes. The link self-test checks link through the mailbox-protected MAC operation and reports failure when `STATUS.LU` is absent.

## State And Persistence
Etthool operations read and write `adapter->msg_enable`, `requested_itr`, `current_itr`, ring `count`, and hardware EITR registers. Stats are derived from `adapter->stats` minus base fields because VF counters do not clear on read.

## Dependencies And Integration Points
The file integrates with netdev-private `igbvf_adapter`, PCI device identity, NAPI/ring resource functions from `netdev.c`, and mailbox-protected link checks in `vf.c`. The callback table is attached to the netdev during probe.

## Risks
Ring resizing is high risk because MSI-X handlers keep ring struct pointers; the code preserves those pointers by copying replacement content into existing ring allocations. Error handling after partial resize still brings the device up, so tests should cover allocation failures. Coalescing writes directly to the RX ring ITR register and must match the interrupt setup state. Stats pointer arithmetic depends on correct offsets and field sizes.

## Test Signals
Use `ethtool -i`, `-k`, `-S`, `-g/-G`, `-c/-C`, `-t`, and `-d` on a VF. Verify ring counts persist across down/up, invalid coalescing values fail with `EINVAL`, unsupported operations return `EOPNOTSUPP`, and stats advance monotonically.
