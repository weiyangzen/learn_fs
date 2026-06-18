# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodePathPair.java

## Purpose
`InodePathPair` is an immutable, closeable pair of `LockedInodePath` objects. It is used when the inode tree needs to hold two path locks at once, for example rename-like operations, while guaranteeing both paths are released together.

## Important APIs, Types, and Functions
The class extends `Pair<LockedInodePath, LockedInodePath>` and implements `AutoCloseable`. Its package-private constructor accepts two locked paths. `setFirst()` and `setSecond()` are overridden to throw `UnsupportedOperationException`, making the pair immutable after construction. `close()` synchronously closes both paths.

## Control Flow, State, and Persistence
There is no persistence. Runtime state is inherited from `Pair`. `InodeTree.lockInodePathPair()` constructs the pair after locking paths in deterministic lexicographic path order; if locking either path fails, that method closes any partial locks before the pair is returned.

## Dependencies and Integration Points
The class depends on the generic Alluxio `Pair` utility and `LockedInodePath`. It integrates with try-with-resources usage around operations that need two locked namespace locations and relies on `LockedInodePath.close()` to flush merged inode journals before releasing locks when configured.

## Risks
`close()` always closes `getFirst()` before `getSecond()`. That is simple and normally correct, but callers must not pass null paths or independently close one side before the pair unless double-close behavior remains safe. The class comment says elements cannot be set once constructed; the constructor is package-private, so immutability depends on only trusted package code creating it.

## Test Signals
Tests should verify mutation methods throw, try-with-resources closes both paths, and exception paths in `InodeTree.lockInodePathPair()` release partially acquired locks. Lock-order tests around rename workloads are the important integration signal.
