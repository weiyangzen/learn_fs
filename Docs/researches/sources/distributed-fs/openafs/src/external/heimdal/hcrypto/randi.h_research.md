# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/randi.h

Purpose: declares internal RAND method descriptors and helper entry points shared among random backend files.

Important APIs/types/functions: extern declarations expose `hc_rand_fortuna_method`, `hc_rand_unix_method`, `hc_rand_egd_method`, `hc_rand_timer_method`, and `hc_rand_w32crypto_method`. It also declares `RAND_timer_method` and `_hc_unix_device_fd`.

Control flow: backend implementations and `rand.c` reference these descriptors for default selection and fallback seeding.

State and persistence: no state is declared beyond extern method objects owned by implementation files.

Dependencies and integration points: included by all `rand-*` implementations. It ties Fortuna fallback logic to Unix, EGD, and timer sources.

Risks and test signals: mismatched extern names or conditional compilation can break method selection. Full build coverage across Windows, Apple, and Unix configurations is the key signal.
