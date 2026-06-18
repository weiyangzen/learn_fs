# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/assert.h

This file is intentionally blank. It satisfies include paths for code that expects an `assert.h` in the kernel hcrypto shim directory while assertions are instead handled in `kernel/config.h` by redefining `assert` to `osi_Assert`.

There are no APIs, state, control flow, or direct dependencies. Integration is include-path compatibility. The risk is only confusion: including this file alone does not provide `assert`. Test signals are successful kernel hcrypto builds and no compilation unit depending on declarations from this blank file.
