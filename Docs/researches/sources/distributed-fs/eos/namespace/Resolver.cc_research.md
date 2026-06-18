## sources/distributed-fs/eos/namespace/Resolver.cc

Purpose: Implements utilities to resolve protobuf or string identifiers into namespace metadata identifiers/objects.

Important APIs and functions: `resolveContainer` accepts a console namespace container specification and returns `IContainerMDPtr`; `retrieveFileIdentifier` parses `fid:`, `fxid:`, `/.fxid:`, and `ino:` strings into a `FileIdentifier`.

Control flow: `resolveContainer` switches on protobuf oneof case: path uses `view->getContainer`, decimal cid parses base 10 then calls container service, hex cxid parses base 16, and empty/unknown throws `MDException(EINVAL)`. `retrieveFileIdentifier` uses prefix checks and converts file inode values through `FileId`.

State and persistence: stateless resolver; returned metadata objects come from view/service caches or backing stores.

Dependencies and integration: depends on `IView`, container service, console protobufs, common parse utilities, `FileId`, XRootD string, and `MDException`.

Risks: `retrieveFileIdentifier` uses `strtoull` without end-pointer validation, so malformed suffixes can partially parse. Container resolve assumes caller holds `eosViewRWMutex`, which is documented but not enforced.

Test signals: cover each protobuf oneof, invalid decimal/hex strings, empty proto exception, all file id prefixes, non-file inode rejection, and malformed string handling expectations.
