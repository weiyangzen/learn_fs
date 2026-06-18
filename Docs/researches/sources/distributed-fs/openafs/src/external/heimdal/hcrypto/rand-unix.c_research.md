# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-unix.c

Purpose: implements a Unix device-backed `RAND_METHOD` using `/dev/urandom` or similar devices.

Important APIs/types/functions: `_hc_unix_device_fd(flags, fn)` probes `/dev/urandom`, `/dev/random`, `/dev/srandom`, and `/dev/arandom`; method callbacks are `unix_seed`, `unix_bytes`, `unix_cleanup`, `unix_add`, `unix_pseudorand`, `unix_status`; `RAND_unix_method` returns the descriptor.

Control flow: reads open the first available random device with `O_NDELAY`, loop until the requested byte count is filled, retry on `EINTR`, and close. Seed/add attempts to open a writable random device and writes caller bytes, ignoring write failure. Status opens and closes a readable device.

State and persistence: no local state is retained. Writes may influence kernel RNG state depending on OS behavior and permissions.

Dependencies and integration points: depends on `rand.h`, `randi.h`, `roken`, Unix file APIs, and `rk_cloexec`. Used directly as the default method on Apple and as an entropy source for Fortuna elsewhere.

Risks and test signals: nonblocking `/dev/random` semantics vary, write-to-device seeding is often ignored or privileged, and every call reopens the device. Tests should cover device probe order, short/interrupted reads, zero/negative sizes, status failure when devices are absent, and cloexec behavior.
