# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/string.h

This file is intentionally blank and serves as a kernel include shim for `string.h`. Required string functions are expected from OpenAFS kernel include sets and roken stubs, not from this file.

There are no APIs, state, or control flow. Integration is include-path compatibility for hcrypto kernel builds. Risks are missing prototypes or platform-specific string availability differences. Test signals are warning-free kernel builds and runtime tests for code paths using `memcpy`, `memset`, `strlen`, and `strcasecmp`.
