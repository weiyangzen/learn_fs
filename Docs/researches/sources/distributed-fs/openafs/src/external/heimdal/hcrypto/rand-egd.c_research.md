# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-egd.c

Purpose: implements a `RAND_METHOD` that talks to an Entropy Gathering Daemon over a Unix-domain socket, plus OpenSSL-compatible `RAND_egd*` helpers.

Important APIs/types/functions: private helpers `connect_egd`, `get_entropy`, `put_entropy`, `get_bytes`; method callbacks `egd_seed`, `egd_bytes`, `egd_cleanup`, `egd_add`, `egd_pseudorand`, `egd_status`; exported `RAND_egd_method`, `RAND_egd`, and `RAND_egd_bytes`.

Control flow: connections default to `/var/run/egd-pool`. Reads send EGD command `0x02` with a maximum 255-byte request and read the exact number of bytes. Writes send command `0x03` with entropy metadata and payload chunks. `RAND_egd_bytes` allocates a buffer, reads bytes from a requested path, seeds the selected global RAND method with them, scrubs the buffer, and frees it.

State and persistence: no persistent local state except the default path string. Entropy is external in the EGD service and, for `RAND_egd_bytes`, transferred into the global RAND subsystem.

Dependencies and integration points: depends on Unix socket APIs when available, `rand.h`, `randi.h`, and `roken` network read/write wrappers. Fortuna uses this as a fallback entropy source when stronger platform sources are unavailable.

Risks and test signals: EGD is legacy and can block or fail; `strlen(path) > sizeof(sun_path)` should arguably be `>=`; `put_entropy` sends zero entropy bits regardless of input quality; exact read/write behavior depends on `net_read/write`. Tests should cover missing socket, custom socket path, chunking over 255 bytes, short reads/writes, and seeding integration.
