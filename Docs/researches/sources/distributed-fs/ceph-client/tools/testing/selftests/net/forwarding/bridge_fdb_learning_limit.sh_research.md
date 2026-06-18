# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_fdb_learning_limit.sh

## Purpose
`bridge_fdb_learning_limit.sh` validates bridge FDB learned-entry accounting and the `fdb_max_learned` limit. It distinguishes dynamic learned entries from static, user, extern-learn, and local entries, and checks which entry types count toward or override learned FDB accounting.

## Important APIs, Functions, and Types
The script sources forwarding `lib.sh`, uses `ip`, `bridge`, `jq`, and `ping_do`, and defines `FDB_TYPES` rows with three fields: entry type, whether it is counted, and whether it overrides an existing learned entry. `fdb_get_n_learned()` reads `fdb_n_learned` from `ip -d -j link show dev br0 type bridge`. `fdb_get_n_mac()` counts matching non-VLAN FDB records. `fdb_add()` abstracts creation of learned, local, static, user (`static use`), and `extern_learn` entries.

## Control Flow
`check_fdb_n_learned_support()` first gates the feature by checking iproute2 help for `fdb_max_learned` and reading `fdb_n_learned` from a temporary bridge. The topology uses six netifs: two host-facing ports, one bridge-only port for local MAC testing, and bridge `br0`. `check_accounting()` resets the FDB, fills learned entries by changing `h1`'s MAC and pinging `h2`, checks the learned count, then runs `check_accounting_one_type()` for every FDB type. `check_limit()` sets `fdb_max_learned`, fills beyond the limit, verifies the cap, and then attempts to insert each FDB type at the limit.

## State and Persistence
The script creates `br0`, enslaves `swp1` and `swp2`, toggles `swp2` learning off, and temporarily enslaves `swp3` when testing local MACs. It repeatedly changes `h1`'s MAC address and resets the bridge FDB. `fdb_reset()` flushes the bridge FDB but reinstalls `h1`'s default MAC as a static `use` entry so dynamic learning starts from a controlled baseline.

## Dependencies and Integration Points
It integrates with the forwarding harness, VRF setup, and common ping helpers. It requires bridge support for `fdb_n_learned` and `fdb_max_learned`, iproute2 JSON details, and a kernel that exposes learned FDB accounting in bridge link info.

## Risks
The learned-entry fill depends on ping traffic creating FDB entries reliably and on `swp2` not learning reply MACs. If bridge output schema changes, `jq` selectors can fail. `bridge fdb flush dev br0` semantics must preserve or remove the expected records before the script reinstalls the default MAC. The limit test assumes `NUM_PKTS` exceeds `FDB_LIMIT` and that learned entries are dropped once the cap is reached.

## Test Signals
Signals include exact `fdb_n_learned` values after reset, fill, add, delete, and override operations; insertion success or rejection at the learned limit depending on entry type; and per-type `log_test` entries documenting accounting and limit behavior.
