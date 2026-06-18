## sources/distributed-fs/ipfs-kubo/test/sharness/t0024-datastore-config.sh

Purpose: verifies datastore spec configuration integrity and daemon behavior when runtime versus on-disk datastore parameters change.

Important control flow: starts and stops a daemon with the existing datastore config, edits runtime-only values in the spec and confirms the daemon can still start, then edits on-disk values and asserts daemon startup fails. Fixtures under `t0024-files` provide alternate specs such as nosync and changed shard functions.

State and dependencies: mutates `.ipfs/config` datastore spec and starts daemons to validate repo opening. Depends on Kubo datastore config parsing and lock/open validation.

Risks: datastore specs are sensitive persistence contracts; allowing incompatible on-disk changes can corrupt or orphan data. Test signal is acceptance of runtime-only changes and rejection of on-disk layout changes.
