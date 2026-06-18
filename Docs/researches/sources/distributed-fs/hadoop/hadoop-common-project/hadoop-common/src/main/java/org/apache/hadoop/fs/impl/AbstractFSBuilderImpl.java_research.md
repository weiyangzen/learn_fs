# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/AbstractFSBuilderImpl.java

## Purpose
Generic FSBuilder base class carrying either a Path or PathHandle plus optional and mandatory configuration options.

## Important APIs, Types, and Functions
Constructors for Optional<Path>/Optional<PathHandle>, Path, PathHandle; opt/must overloads for strings, primitives, arrays; getOptions(), getMandatoryKeys(), getOptionalKeys(), rejectUnknownMandatoryKeys().

## Control Flow
Construction rejects providing both path and path handle. opt removes the key from mandatory and records it optional; must records it mandatory and may remove optional for arrays. Values are stored in a non-default-loading Configuration. rejectUnknownMandatoryKeys checks all mandatory keys against known keys.

## State and Persistence Behavior
Stores immutable optional path/pathHandle and mutable option Configuration plus key sets. No persistence.

## Dependencies and Integration Points
Base for FutureDataInputStreamBuilderImpl, MultipartUploaderBuilderImpl, and filesystem-specific builders.

## Risks and Test Signals
Risks are type narrowing in float/double overloads that call optLong/mustLong, mandatory/optional set consistency, and unknown-key validation order. Tests should cover all overloads, path/pathHandle exclusivity, and mandatory rejection.
