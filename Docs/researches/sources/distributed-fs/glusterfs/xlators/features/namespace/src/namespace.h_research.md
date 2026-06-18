# sources/distributed-fs/glusterfs/xlators/features/namespace/src/namespace.h

## Purpose

`namespace.h` defines the private types used by the namespace translator.

## Important APIs, Types, and Functions

It defines `GF_NAMESPACE`, `ns_private_t` with `tag_namespaces`, and `ns_local_t` with a fake `loc_t` plus a `call_stub_t *` used while resolving ancestry paths.

## Control Flow

No executable control flow is present.

## State and Persistence Behavior

`ns_private_t` is stored in `this->private`; `ns_local_t` is temporary request state for the fallback getxattr path. Neither is persisted to disk.

## Dependencies and Integration Points

The header includes `config.h` and Gluster call-stub definitions, and it relies on Gluster `loc_t` and boolean types being available through the translation unit includes.

## Risks and Edge Cases

Because `ns_local_t` owns a copied/fake loc and a call stub, cleanup must always wipe the loc and resume or destroy the stub exactly once. Changes to `frame->root->ns_info` layout outside this header affect namespace behavior even though the type is not declared here.

## Test Signals

Compile coverage and fallback ancestry tests validate allocation and cleanup of `ns_local_t`, while init/reconfigure tests validate `ns_private_t` handling.
