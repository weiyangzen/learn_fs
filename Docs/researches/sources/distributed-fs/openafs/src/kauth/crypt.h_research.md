# sources/distributed-fs/openafs/src/kauth/crypt.h

## Purpose
Declares the local `crypt` compatibility function used by the kauth Windows string-to-key path.

## Important APIs, Types, And Functions
The header only defines the include guard `__CRYPT_H_ENV__` and declares `char *crypt(char *, char *)`.

## Control Flow
There is no runtime control flow. Including code calls `crypt` in `crypt.c` to produce legacy DES password-hash material.

## State And Persistence
The header stores no state. The declaration exposes a function whose implementation returns static process-local state.

## Dependencies And Integration Points
It is an integration shim for callers that need a `crypt` declaration on platforms without a suitable system header. It must stay ABI-compatible with the implementation in `crypt.c`.

## Risks And Test Signals
The prototype uses non-const `char *` parameters while `crypt.c` defines `const char *`; strict-prototype builds are the main signal for drift. Functional coverage comes from callers that include the header and link against the local implementation.
