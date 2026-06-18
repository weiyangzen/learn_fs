## sources/distributed-fs/eos/mgm/bulk-request/utils/PrepareArgumentsWrapper.hh

Purpose: wraps construction and cleanup of `XrdSfsPrep` arguments through protobuf utilities. It is useful for tests or callers that need to build prepare requests programmatically.

Important APIs: constructors from request ID/options with optional paths/oinfos, destructor deleting generated `XrdSfsPrep`, `addFile()`, `getNbFiles()`, and `getPrepareArguments()`.

State/dependencies: stores `eos::auth::XrdSfsPrepProto` and a raw `XrdSfsPrep*` generated on demand. Risks include repeated `getPrepareArguments()` overwriting `mPargs` without freeing a previous generated object first, and path/oinfo count mismatches if callers use constructors/adders inconsistently. Tests should cover lifetime cleanup, repeated generation behavior, and path/opaque ordering.
