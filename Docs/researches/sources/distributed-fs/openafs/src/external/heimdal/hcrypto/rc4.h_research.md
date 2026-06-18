# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc4.h

Purpose: declares RC4 key state and APIs.

Important APIs/types/functions: `RC4_KEY` contains stream indices `x`/`y` and 256-word state array. The header renames and declares `RC4_set_key` and `RC4`.

Control flow: callers initialize `RC4_KEY` once per stream and pass it through one or more `RC4` calls.

State and persistence: all stream state is in `RC4_KEY` and mutates for each byte processed.

Dependencies and integration points: consumed by `rc4.c` and EVP RC4 provider descriptors.

Risks and test signals: ABI layout and legacy algorithm exposure are risks. ARCFOUR vectors and segmented-stream tests validate behavior.
