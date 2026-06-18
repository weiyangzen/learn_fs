# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/lock/FuseReadWriteLockManager.java

Purpose: per-path read/write lock manager for JNI FUSE streams.

Important APIs and flow: `tryLock(path, mode)` hashes the path with MD5, obtains a weakly cached `ClientRWLock`, chooses read or write lock, waits up to 20 seconds, and returns a `CloseableResource<Lock>` that unlocks on close. Interrupted waits restore the interrupt flag and throw cancellation.

State, dependencies, risks, and tests: state is a Guava `LoadingCache<String, ClientRWLock>` with weak values and max reader concurrency 64 per path. It depends on Alluxio concurrency primitives and runtime exceptions. Risks include MD5 collision theoretical aliasing, weak-value lock eviction subtleties, timeout surfacing as stream creation failure, and no direct rename coordination. Tested indirectly by stream open/create behavior and unmount waiting.
