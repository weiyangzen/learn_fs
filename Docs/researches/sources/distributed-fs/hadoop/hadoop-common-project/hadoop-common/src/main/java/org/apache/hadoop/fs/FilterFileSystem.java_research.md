# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FilterFileSystem.java

Purpose: `FilterFileSystem` is the stable public wrapper base class for decorating an old-style `FileSystem`. By default it delegates nearly every operation to a contained `FileSystem`, allowing subclasses to intercept behavior selectively without reimplementing the full API.

Important APIs: constructors, `getRawFileSystem`, `initialize`, `makeQualified`, `checkPath`, open/create/append/rename/delete/list methods, working directory and status methods, checksum, symlink, ACL, xattr, snapshot, storage policy, trash, builder, async open, and capability APIs.

Control flow and state: the wrapper stores `protected FileSystem fs` and optional `swapScheme`. `initialize` initializes the wrapped filesystem if needed and records a scheme replacement when wrapper and wrapped schemes differ. `makeQualified` delegates then rewrites the scheme when `swapScheme` is set. Most methods forward directly; `close` closes both super and wrapped fs. `hasPathCapability` explicitly masks multipart uploader and experimental batch listing even if the wrapped filesystem reports support.

Dependencies and integration: sits between clients and wrapped `FileSystem` implementations. It preserves shared statistics by copying `fs.statistics`, exposes the child through `getChildFileSystems`, and participates in newer builder APIs via `createFile`, `appendFile`, `openFile`, and `openFileWithOptions`.

Risks: subclasses depend on comprehensive delegation; missing overrides can bypass wrapper behavior. Scheme swapping notes authority handling is imperfect. Capability masking can surprise wrappers that genuinely support multipart or batch listing through subclass logic unless overridden. Closing the wrapper closes the child and can affect shared wrapped instances.

Test signals: verify delegation coverage, initialization of unconfigured children, scheme rewrite behavior, path capability masking, child filesystem reporting, close propagation, and subclass overrides around create/open/delete paths.
