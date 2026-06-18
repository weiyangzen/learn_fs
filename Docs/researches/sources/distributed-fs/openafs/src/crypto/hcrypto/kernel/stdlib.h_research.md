# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/stdlib.h

This file is intentionally blank and acts as a kernel include shim for code that includes `stdlib.h`. Actual allocation and abort behavior is supplied by macro remapping in `kernel/config.h`.

There are no APIs or state here. Integration is include-path compatibility for kernel hcrypto. Risks appear if a kernel-compiled source expects standard library declarations not provided by `config.h`. Test signals are compile coverage and no implicit declaration warnings for allocation or abort calls.
