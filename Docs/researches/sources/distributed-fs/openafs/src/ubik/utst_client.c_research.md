
# sources/distributed-fs/openafs/src/ubik/utst_client.c

`utst_client.c` is a simple sample/test client for the Ubik test service generated from `utst_int.xg`. It demonstrates parsing a server list, creating null-security Rx connections to USER service id on port 3000, initializing a Ubik client, and invoking sample RPCs through generated client wrappers.

The main commands are `-inc`, `-try`, `-qget`, `-get`, `-trunc`, `-minc`, and `-mget`. Single-shot commands call `ubik_SAMPLE_Inc`, `ubik_SAMPLE_Test`, `ubik_SAMPLE_QGet`, `ubik_SAMPLE_Get`, or `ubik_SAMPLE_Trun`. Looping modes repeatedly interleave get and increment calls with one-second sleeps to expose failover and race behavior.

There is no local persistence. State is the `struct ubik_client`, Rx connection array, and returned integer sample value. Dependencies are `ubik_ParseClientList`, Rx null security, generated sample stubs, and platform sleep/select differences.

Risks are limited because it is a test utility: infinite loops in `-minc`/`-mget`, null authentication, hard-coded port 3000, and sparse argument validation. Test signals are manual integration tests against `utst_server`: read/write/truncate behavior, quick read-any get, repeated sync-site discovery, and behavior while servers are restarted or partitioned.
