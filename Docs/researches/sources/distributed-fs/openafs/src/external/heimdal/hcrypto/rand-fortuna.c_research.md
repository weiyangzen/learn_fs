# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-fortuna.c

Purpose: implements a Fortuna-like PRNG `RAND_METHOD` using SHA-256 entropy pools and AES-256 counter-mode output.

Important APIs/types/functions: `FState` stores counter, result block, key, 32 SHA-256 pools, AES key schedule, reseed metadata, pool0 byte count, random pool cursor, startup flag, and pid. Core helpers include `init_state`, `add_entropy`, `reseed`, `extract_data`, `rekey`, `startup_tricks`, `fortuna_reseed`, `fortuna_init`, and method callbacks `fortuna_seed`, `fortuna_bytes`, `fortuna_cleanup`, `fortuna_add`, `fortuna_pseudorand`, `fortuna_status`. Exported `RAND_fortuna_method` returns `hc_rand_fortuna_method`.

Control flow: initialization creates empty pools and attempts an initial seed. Entropy is hashed before being added to pool 0 before first reseed or a key-selected pool afterward. Reseed is gated by pool0 fill/time rules, mixes selected pool digests, old key, and pid into a new key, then resets pool0 byte accounting. Extraction reseeds when needed, performs one-time startup randomization, detects forks by pid, emits AES(counter) blocks, periodically rekeys for large requests, and rekeys at the end of every request. The public bytes path locks a global mutex, initializes if needed, triggers extra reseeds after `FORTUNA_RESEED_BYTE`, extracts, and unlocks.

State and persistence: global `main_state`, `init_done`, `have_entropy`, `resend_bytes`, and `fortuna_mutex` persist process-local PRNG state. Cleanup zeros `main_state` and resets flags. No state is saved to disk by this file.

Dependencies and integration points: depends on Heimdal thread mutexes, `randi.h`, AES, SHA-256, Unix/EGD/timer random methods, `arc4random` when available, `/etc/shadow` fallback reads, pid/time/uid entropy, and `rand.c` default method selection on non-Apple Unix.

Risks and test signals: fallback entropy marks success even for weak timer/metadata inputs, `/etc/shadow` read size handling hashes full buffer size instead of bytes read, global mutex serialization can bottleneck callers, and fork/reseed behavior is security-critical. Tests should cover initial seeding success/failure, deterministic hooks for add/extract, fork pid change, cleanup/reinit, concurrent `RAND_bytes`, large request rekeying, and operation when Unix/EGD sources are unavailable.
