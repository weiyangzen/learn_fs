# sources/cloud-native/nydus/storage/src/remote/mod.rs

Purpose: declares the remote blob manager module boundary for storage and re-exports the public client/server entry points.

Important APIs/types/functions: `pub use self::client::RemoteBlobMgr` exposes the remote blob manager client, and `pub use self::server::Server` exposes the server type. Internal submodules are `client`, `connection`, `message`, and `server`.

Control flow: there is no executable control flow in this file. It is a namespace and visibility shim that lets callers import `crate::remote::RemoteBlobMgr` and `crate::remote::Server` while keeping connection/message internals private to the module tree.

State and persistence: none.

Dependencies and integration points: ties together the unlisted `client` and `connection` modules with the researched `message.rs` and `server.rs`. Storage users depend on this file for the public remote API surface.

Risks: because `message` and `connection` are private, protocol extension must happen inside this module. Re-exporting only two types keeps API narrow but can hide lower-level testing hooks from external integration tests.

Test signals: no direct tests. It is indirectly compiled by remote server/client tests.
