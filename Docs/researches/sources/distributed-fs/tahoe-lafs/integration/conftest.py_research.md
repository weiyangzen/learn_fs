## sources/distributed-fs/tahoe-lafs/integration/conftest.py

Purpose: pytest fixture hub for Tahoe-LAFS integration tests, building shared grids, clients, Tor resources, and logging.

Important APIs/fixtures: `pytest_addoption`, `pytest_collection_modifyitems`, `eliot_logging`, `reactor`, `port_allocator`, `temp_dir`, `flog_binary`, `flog_gatherer`, `grid`, `introducer`, `introducer_furl`, `tor_introducer`, `tor_introducer_furl`, `storage_nodes`, `alice`, `bob`, `chutney`, `ChutneyTorNetwork`, and `tor_network`.

Control flow: options control temp retention, coverage, Foolscap forcing, and slow-test selection. Session fixtures create a temp directory, flog gatherer, introducer, grid, five storage nodes, clients, and optional Tor/Chutney network. Finalizers stop processes, dump logs, and remove tempdirs unless retained.

State and dependencies: writes `integration.eliot.json`, temp Tahoe node directories, pid/config files, flog logs, and Tor network state. Depends on Twisted, pytest-twisted, Eliot, Foolscap, Chutney, Tor binaries, Tahoe node helpers, and port allocation.

Risks: session-scoped shared mutable grid can cause test interference. Tor setup is slow and environment-sensitive. The file sets global environment variables for Tahoe HTTP timeout and Foolscap logging at import time.
