# sources/distributed-fs/lizardfs/src/master/mfsrestoremaster.in

## Purpose

`mfsrestoremaster.in` is a Bash template script that promotes a metalogger host into a spare master by restoring metadata from metalogger backups, moving the master IP to a network interface, and starting `mfsmaster`. The source was read as a complete 158-line script.

## Important APIs, Types, and Functions

Shell helpers are `notice`, `panic`, `get_config_option`, `if_equal`, and `is_tcp_port_open`. The script consumes `<net-interface>` and optional `<etc-mfs-dir>`, reads `mfsmetalogger.cfg` and `mfsmaster.cfg`, uses `mfsmetarestore`, `ifconfig`, and `mfsmaster`, and relies on configured template paths `@ETC_PATH@` and `@DATA_PATH@`.

## Control Flow

After argument and root checks, it loads metalogger/master config paths, validates readable configs, resolves the intended master host from metalogger `MASTER_HOST` and master MATOML/MATOCS/MATOCL listen addresses, verifies no host or TCP service already owns the address, restores `metadata.mfs` from `metadata_ml.mfs.back` plus `changelog_ml.*`, assigns the IP address to the requested interface, and starts the master server with the selected config.

## State and Persistence Behavior

It writes the restored master metadata file in the master data path, changes host network interface state, and starts a daemon. It does not update configs itself. Failures call `panic` and abort before starting master, but side effects before a later failure, such as restored metadata or changed interface address, may remain.

## Dependencies and Integration Points

Dependencies include Bash with `set -e -u`, `awk`, Python socket module, `ping`, `mfsmetarestore`, `ifconfig`, and `mfsmaster`. It bridges metalogger backup data and master startup in failover operations.

## Risks and Edge Cases

The config parser is simple AWK matching and ignores include/quoting complexities. `ifconfig $net_interface $master_host` is unquoted for the interface. TCP reachability and ping checks are race-prone. If restoration succeeds but interface or daemon startup fails, cleanup is manual. The script assumes legacy network tooling and Python availability.

## Test Signals

Shellcheck-like static checks, dry-run tests with fixture configs, mocked command-path tests for restore/interface/start failure points, and integration drills on a test network where the target IP is free.
