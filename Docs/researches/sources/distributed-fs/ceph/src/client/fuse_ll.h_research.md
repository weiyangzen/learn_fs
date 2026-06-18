# sources/distributed-fs/ceph/src/client/fuse_ll.h

## Purpose
`fuse_ll.h` declares the public `CephFuse` wrapper around the low-level FUSE adapter implementation.

## Important APIs, Types, and Functions
`CephFuse` exposes constructor/destructor, `init()`, `start()`, `mount()`, `loop()`, `finalize()`, nested `Handle`, and `get_mount_point()`. It stores an owning raw pointer to `CephFuse::Handle`.

## Control Flow
Callers construct with a `Client*` and success-signal fd, initialize using process arguments, start the FUSE session, enter the loop, then finalize.

## State and Persistence Behavior
The header exposes no persistent state. The private handle owns FUSE session objects and callback state in the implementation.

## Dependencies and Integration Points
It requires `Client` and standard string declarations from includers. `CephFuse` marks the client as a FUSE client in its implementation constructor.

## Risks
The declared `mount()` method has no implementation in the researched file, so callers should use `start()` unless another translation unit provides it. The raw pointer requires destructor/finalize discipline.

## Test Signals
Build/link tests should catch the `mount()` declaration if referenced. Lifecycle tests should call init/start/loop/finalize in expected daemon paths.
