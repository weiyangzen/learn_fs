## sources/distributed-fs/tahoe-lafs/integration/grid.py

Purpose: object model and process orchestration helpers for integration-test Tahoe grids.

Important APIs/classes: `FlogGatherer`, `create_flog_gatherer`, `StorageServer.restart`, `create_storage_server`, `Client.reconfigure_zfec`, `Client.restart`, `Client.add_sftp`, `create_client`, `Introducer`, `_validate_furl`, `create_introducer`, `Grid.add_storage_node`, `Grid.add_client`, and `create_grid`.

Control flow: helpers spawn flog gatherer and `twistd`, create introducers and nodes through Tahoe runner utilities, wait for readiness strings/furls, register cleanup finalizers, and wrap process transports/protocols in attr classes. `Grid` allocates ports, adds storage nodes and clients, and stores them in lists/maps. `Client.add_sftp` creates an alias, generates SSH keys, writes SFTP config/accounts, and restarts the node.

State and dependencies: creates temp directories, Tahoe configs, private keys, accounts files, flog dumps, running processes, and client/server node state. Depends on Twisted deferreds/process protocols, Foolscap furl decoding, Eliot, attrs validators, pytest-twisted, and integration util helpers.

Risks: many methods mutate live object process/protocol fields on restart. Furl validation prevents hangs from missing location hints. Cleanup must handle process termination races and log dumping failures.
