# sources/distributed-fs/openafs/src/crypto/hcrypto/heim_threads.h

This userspace hcrypto threading shim maps Heimdal mutex macros to pthread mutexes under `AFS_PTHREAD_ENV`, and to no-op integer locks otherwise. The no-op path is justified by comments that the PRNG code does not yield or use the LWP IO manager, so it cannot be preempted under the LWP model.

The API consists of `HEIMDAL_MUTEX`, `HEIMDAL_MUTEX_INITIALIZER`, and init/lock/unlock/destroy macros. There is no independent state beyond mutex objects in users. Dependencies are pthreads when enabled and OpenAFS threading model assumptions when not.

Integration is with hcrypto random and global-state code. Risks are concurrency assumptions: if hcrypto gains yielding or I/O behavior in non-pthread builds, the no-op locks become unsafe. Test signals are pthread race tests for PRNG access, LWP builds, and review of hcrypto call paths for blocking/yielding changes.
