# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand.c

Purpose: provides the OpenSSL-compatible global RAND API and method selection layer.

Important APIs/types/functions: global APIs include `RAND_seed`, `RAND_bytes`, `RAND_cleanup`, `RAND_add`, `RAND_pseudo_bytes`, `RAND_status`, `RAND_set_rand_method`, `RAND_get_rand_method`, `RAND_set_rand_engine`, `RAND_load_file`, `RAND_write_file`, and `RAND_file_name`. Static `selected_meth` and `selected_engine` hold the active source.

Control flow: `init_method` lazily selects Windows CryptoAPI on `_WIN32`, Unix device random on Apple, and Fortuna elsewhere. Public operations initialize if needed and dispatch to the method callbacks. Method changes clean up the previous method and release any selected engine. Engine selection uprefs the engine, fetches its RAND method, and replaces the global method. Random file loading reads chunks and seeds the method; writing emits 1024 bytes from `RAND_bytes`; filename selection uses `RANDFILE`, `HOME`, Unix random devices, or Windows local app data.

State and persistence: process-global selected method/engine persist until cleanup or replacement. `RAND_load_file` and `RAND_write_file` interact with caller-specified random state files; `RAND_file_name` only chooses a path.

Dependencies and integration points: depends on `rand.h`, `randi.h`, `engine.h`, `roken`, OS file APIs, and Windows shell APIs when built on Windows. Used by EVP random key generation and DES random key helpers.

Risks and test signals: no locking protects global method/engine changes, file load treats `size` as minimum but returns success after any bytes, state-file writes do not use atomic replacement, and default method varies by platform. Tests should cover default selection, zero-size requests, method replacement cleanup, engine failure, random file read/write permissions, filename selection under setuid restrictions, and concurrent callers if supported.
