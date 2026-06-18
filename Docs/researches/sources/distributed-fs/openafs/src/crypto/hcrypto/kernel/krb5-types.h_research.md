# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/krb5-types.h

This file is empty. It satisfies an include expected by hcrypto or Heimdal-derived kernel code, while the actual minimal Kerberos types are supplied by `src/crypto/rfc3961/rfc3961.h` and `krb5_locl.h`.

There are no APIs, state, or dependencies. Integration is include-path compatibility. The main risk is accidental reliance on it for type definitions; test signals are compile coverage ensuring required Kerberos types come from the RFC3961 headers.
