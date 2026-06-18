# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/delegating/DelegatingUnderFileSystem.java

Purpose: test utility `UnderFileSystem` wrapper that delegates every method to another UFS. Subclasses can override selected operations to inject behavior while inheriting pass-through coverage for the rest of the interface.

Important APIs and control flow: the constructor stores `mUfs`. Methods forward lifecycle, create/delete, status, ACL, location, list, mkdir/open/rename, owner/mode, active sync, async listing, rate limiter, physical store, and capability calls directly to `mUfs`. It includes overloads for existing/nonexisting file operations and nullable iterable/listing methods.

State, dependencies, integration, risks, tests: state is the wrapped UFS reference; persistence and external state remain entirely in the delegate. Dependencies span the full Alluxio UFS interface: ACL types, statuses, options, sync info, rate limiter, and async callbacks. Risk is interface drift: new `UnderFileSystem` methods must be added here or subclasses stop compiling. It is not thread-safe beyond the delegate's behavior.
