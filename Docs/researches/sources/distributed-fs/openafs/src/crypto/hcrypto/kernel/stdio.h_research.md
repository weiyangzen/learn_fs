# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/stdio.h

This file is intentionally blank. It exists to satisfy include paths for userspace-derived code that includes `stdio.h` while compiling in kernel mode, where real stdio is unavailable or inappropriate.

There are no APIs, state, or control flow. Integration is include-path masking for kernel hcrypto. Risks are compile or behavior failures if code expects `FILE`, `printf`, or other stdio declarations. Test signals are successful kernel hcrypto builds and review that no kernel-compiled hcrypto source actually uses stdio APIs.
