## sources/distributed-fs/ipfs-kubo/test/sharness/t0120-bootstrap.sh

Purpose: tests `ipfs bootstrap` list/add/remove operations offline and through a running daemon.

Important APIs and helpers: defines fixed bootstrap peers `BP1` through `BP7`, helper `test_bootstrap_list_cmd`, and helper `test_bootstrap_cmd`. It uses `ipfs bootstrap`, `bootstrap list`, `bootstrap add`, `bootstrap rm`, `bootstrap rm --all`, stdin input, `test_cmp`, and daemon lifecycle helpers.

Control flow and state: clears all bootstrap peers, verifies empty listing, adds peers by arguments, verifies exact output and persisted ordering, removes selected peers, rejects a malformed peer, removes all, then repeats add/remove using stdin. The whole sequence runs once offline and once with the daemon online.

Dependencies and integration points: covers config persistence for `Bootstrap`, multiaddr validation, command output stability, stdin parsing, and daemon-vs-offline command routing.

Risks and test signals: catches bootstrap config drift, broken batch input, bad error handling for invalid peers, and output changes that can break scripts. Signals are exact `added`/`removed` lines and list output equality.
