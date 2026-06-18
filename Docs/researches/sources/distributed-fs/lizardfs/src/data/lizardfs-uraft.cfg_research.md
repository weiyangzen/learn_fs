# sources/distributed-fs/lizardfs/src/data/lizardfs-uraft.cfg

Purpose: sample configuration for the LizardFS uRaft high-availability daemon.

Important settings: `URAFT_PORT`, `URAFT_STATUS_PORT`, repeated `URAFT_NODE_ADDRESS`, `URAFT_ID`, local master address/port, election timeout bounds, heartbeat period, local master health-check period, and floating IP/netmask/interface settings.

Control flow: the uRaft daemon reads these values to identify cluster peers, elect a leader, monitor the local master, and manage a floating service IP; all sample values are commented.

State and persistence: administrator-edited persistent HA configuration; no state is active in the sample.

Dependencies and integration: installed into the uRaft examples directory by the data CMake file; coordinates with local master `MATOCL` endpoint and network interface configuration.

Risks: incorrect node order/ID, timeouts, or floating IP settings can break failover or create network conflicts. The file documents defaults but does not validate topology.

Test signals: no direct tests in this subset; behavior depends on uRaft daemon config parsing and HA integration tests.
