<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/threading/AtomicInt64.h -->
## sources/distributed-fs/beegfs/client_module/source/common/threading/AtomicInt64.h

**Purpose:** Wraps Linux `atomic64_t` with fallback initialization for older kernels. **APIs/types:** `AtomicInt64` stores `atomic64_t`; inline init/uninit, inc/read, inc, dec, read, and set helpers. Disabled code documents compare-and-swap and max helpers unavailable on old kernels. **Control flow/state:** operations delegate directly to kernel atomic64 APIs. **Dependencies/integration:** includes `os/atomic64.h` when `ATOMIC64_INIT` is missing. **Risks/tests:** portability across old kernels is the main concern; tests should compile both macro paths and validate 64-bit counter increments/decrements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/threading/AtomicInt64.h -->
