# sources/distributed-fs/ceph-client/drivers/net/wireguard/ratelimiter.h

Purpose: Declares the WireGuard handshake ratelimiter lifecycle and allow-check API.

Important APIs: `wg_ratelimiter_init()`, `wg_ratelimiter_uninit()`, and `wg_ratelimiter_allow()`. DEBUG builds also declare `wg_ratelimiter_selftest()`.

Control flow: Header-only declarations are used by device initialization/destruction and receive/cookie handling.

State and persistence: No state in the header; implementation owns global refcounted tables.

Dependencies and integration points: Includes skb type declarations and is consumed by `device.c`, `receive.c`/cookie paths, `main.c` DEBUG selftests, and `ratelimiter.c`.

Risks: Callers must initialize before allow checks and balance uninit calls across devices.

Test signals: Compile in DEBUG and non-DEBUG builds, module load selftest, and device create/destroy cycles.
