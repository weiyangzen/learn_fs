<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cred.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/cred.rs

## Purpose
This file wraps kernel credentials (`struct cred`) for Rust code.

## Important APIs, Types, and Functions
`Credential` is a transparent wrapper over `Opaque<bindings::cred>`. It exposes unsafe `from_ptr`, `as_ptr`, `get_secid`, and `euid`. It implements `Send`, `Sync`, and `AlwaysRefCounted`.

## Control Flow and State
`from_ptr` casts a valid C credential pointer into a borrowed Rust reference. `get_secid` initializes a local `secid`, calls `security_cred_getsecid`, and returns the resulting security ID. `euid` reads the immutable effective UID field and wraps it as `Kuid`. Refcount methods call `get_cred` and `put_cred`.

## State and Persistence Behavior
Credentials are reference-counted C objects. The wrapper does not mutate credential fields and relies on the kernel model where credentials are mostly immutable after initialization and changes happen by replacing credential pointers. `ARef<Credential>`-style ownership is enabled through `AlwaysRefCounted`.

## Dependencies and Integration Points
The module depends on `bindings`, `AlwaysRefCounted`, `task::Kuid`, and `Opaque`. It integrates with security hooks and task/file credential users that need stable references.

## Risks
`from_ptr` is unsafe because validity and lifetime are caller-provided. `get_secid` depends on security subsystem behavior. `Send`/`Sync` rely on credential immutability and C-side synchronization; adding mutable accessors would need new analysis. Refcount underflow/double-put would be a serious lifetime bug.

## Test Signals
No local tests. Runtime signals should include correct UID/security ID reads and balanced get/put behavior under `ARef` use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cred.rs -->
