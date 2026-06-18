# sources/distributed-fs/ceph-client/arch/arm64/mm/mem_encrypt.c

## Purpose
This file is a top-level dispatcher for ARM64 memory encryption and decryption APIs. It deliberately avoids hard-coding the low-level implementation because details differ across confidential-computing environments such as pKVM or CCA.

## Important APIs, Types, and Functions
The important interfaces are `arm64_mem_crypt_ops_register()`, `set_memory_encrypted()`, and `set_memory_decrypted()`. The registered implementation is a `const struct arm64_mem_crypt_ops *crypt_ops` with `encrypt` and `decrypt` methods.

## Control Flow
Platform or realm-specific code calls `arm64_mem_crypt_ops_register()` once; duplicate registration returns `-EBUSY` and warns. `set_memory_encrypted()` and `set_memory_decrypted()` return success immediately when no ops are registered or the address alignment warning fires. Otherwise they dispatch to the registered `encrypt()` or `decrypt()` callback.

## State and Persistence
`crypt_ops` is the only persistent state. It is effectively a singleton process-wide hook for the architecture memory encryption API.

## Dependencies and Integration Points
This file integrates with generic memory encryption callers through exported GPL symbols and with ARM64 platform code through `<asm/mem_encrypt.h>`. In this source set, `pageattr.c` registers Realm operations using this hook.

## Risks
The dispatcher treats no registered operations as success, which is correct for systems without encryption transitions but can hide missing registration on systems that expected one. Alignment violations only warn and return success because the early guard condition is shared with the no-op case. Callback implementations must provide the real state transition and page-table synchronization.

## Test Signals
Confidential-computing tests should verify successful registration, duplicate registration failure, and actual encrypt/decrypt transitions through the registered callbacks. Non-confidential boots should exercise callers that expect no-op success.
