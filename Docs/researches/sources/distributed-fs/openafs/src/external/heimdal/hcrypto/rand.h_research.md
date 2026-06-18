# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand.h

Purpose: declares the hcrypto RAND compatibility API and `RAND_METHOD` callback table.

Important APIs/types/functions: `struct RAND_METHOD` contains seed, bytes, cleanup, add, pseudorand, and status callbacks. The header declares global RAND APIs, EGD helpers, method factories for Fortuna/Unix/EGD/Windows, and symbol renames to `hc_*`.

Control flow: callers either use the global RAND functions or install a method/engine; method implementations supply the callback behavior.

State and persistence: no state is defined here, but the method table describes the stateful callback contract implemented by `rand.c` and `rand-*` files.

Dependencies and integration points: includes `hcrypto/engine.h` and is consumed by EVP, DES random key generation, provider code, and platform random implementations.

Risks and test signals: callback signatures use `int` sizes while public functions use `size_t`, so very large sizes require care in dispatching implementations. Compile coverage and RAND method smoke tests validate integration.
