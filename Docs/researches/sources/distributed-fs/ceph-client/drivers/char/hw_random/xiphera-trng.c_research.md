# sources/distributed-fs/ceph-client/drivers/char/hw_random/xiphera-trng.c

Purpose: Xiphera FPGA TRNG hwrng driver for `xip8001b-trng`.

Important APIs, types, and functions: `struct xiphera_trng`, `xiphera_trng_read()`, `xiphera_trng_probe()`, OF match table, and platform driver registration.

Control flow: probe maps registers, resets the TRNG, waits briefly for reset ack with one retry, releases reset, enables, zeroizes, waits for startup tests, acknowledges zeroize, and registers hwrng with quality 900. Read loops while full words fit and status is `TRNG_NEW_RAND_AVAILABLE`, reads a word, sends READ and ENABLE commands, and returns bytes read.

State and persistence: per-device mapped register base and hwrng object. Hardware startup and zeroize state are initialized at probe only.

Dependencies and integration: platform/OF, MMIO, sleeps/delays, hwrng.

Risks and test signals: read ignores `wait`, so consumers may receive 0 if data is not ready. Startup status is read multiple times and may change between checks. Tests should cover reset ack retry/failure, startup failure/no response, read-ready loop, register command ordering, and registration failure.
