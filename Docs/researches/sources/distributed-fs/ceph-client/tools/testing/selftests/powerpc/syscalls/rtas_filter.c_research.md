# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/rtas_filter.c

Purpose: tests kernel filtering of the powerpc RTAS syscall, ensuring permitted calls pass and prohibited or out-of-RMO buffers are rejected.

Important APIs/types/functions: `struct rtas_args`, `struct region`, `get_property()`, `rtas_token()`, `read_kregion_bounds()`, `rtas_call()`, and `test()` are core.

Control flow: helper functions read RTAS tokens from `/proc/device-tree/rtas`, build big-endian RTAS argument blocks, and call `__NR_rtas`. The test checks `get-time-of-day`, `nvram-fetch`, reads `/proc/ppc64/rtas/rmo_buffer`, then probes permitted and invalid buffer ranges for RTAS calls.

State and persistence behavior: reads firmware/procfs state only; no persistent RTAS mutation is intended.

Dependencies and integration points: requires powerpc RTAS firmware interfaces, procfs/device-tree paths, and `utils.c` file allocation helpers.

Risks and test signals: unavailable RTAS calls are treated as skip-like acceptable outcomes. Buffer-boundary checks depend on parsing RMO region data accurately.
