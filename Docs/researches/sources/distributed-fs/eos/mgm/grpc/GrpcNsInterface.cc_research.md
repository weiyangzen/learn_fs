# sources/distributed-fs/eos/mgm/grpc/GrpcNsInterface.cc

## Purpose
Implements the gRPC namespace bridge for EOS MGM, translating RPC metadata, find, insert, namespace-stat, and namespace command requests into existing MGM namespace, proc command, ACL, recycle, quota, token, and filesystem APIs.

## Important APIs, types, and functions
`Filter()` applies `MDSelection` predicates to file and container metadata. `GetMD()` streams file or container metadata responses and fills protobuf fields, checksums, xattrs, paths, etags, locations, and timestamps. `Stat()`, `StreamMD()`, and `Find()` implement metadata lookup, listing, and breadth-by-depth traversal. `Access()` applies UNIX permissions and EOS ACL checks. `NsStat()` reports namespace and process health. `FileInsert()` and `ContainerInsert()` create metadata as sudo-only operations. `Exec()` dispatches namespace commands to `Mkdir`, `Rmdir`, `Touch`, `Unlink`, `Rm`, `Rename`, `Symlink`, `SetXAttr`, `Version`, recycle commands, `Chown`, `Chmod`, `Acl`, `Token`, and `Quota`.

## Control flow
Requests optionally remap the caller identity if the authenticated identity is sudo-capable. Metadata paths prefetch namespace records, take read locks when needed, check parent or self access, filter, then stream protobuf responses. Mutation commands resolve path or id inputs, delegate to `gOFS` or command objects, and encode return codes/messages into the RPC reply while usually returning `grpc::Status::OK`.

## State and persistence
This file can create and update namespace file/container metadata, set xattrs, mutate ACLs, create/purge/grab versions, remove or recycle files, chown/chmod paths, create tokens, and set/remove quota entries. It also reads process memory/fd stats. Locks are taken around namespace view reads/writes.

## Dependencies and integration points
Compiled under `EOS_GRPC`. Depends on generated RPC protobufs, gRPC server writer/status, `gOFS`, namespace services, `Prefetcher`, `Acl`, proc command wrappers, recycle/quota/token command classes, Linux process-stat helpers, checksum/layout helpers, etag helpers, regex, and XRootD error structures.

## Risks and test signals
Several command handlers return application errors in reply payloads rather than gRPC error statuses, so clients must inspect both. File filtering appears to check `mtime` twice and uses `mtime` for `locations()` range filtering, which may be unintended. Mutation coverage is broad and security-sensitive; tests should cover sudo remapping, ACL/immutable behavior, path-vs-id resolution, filter edge cases, recursive xattr, version operations, recycle list/restore/purge, quota parsing, insert conflict detection, and lock behavior during streamed listings.
