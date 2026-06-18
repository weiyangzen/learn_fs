# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/XAttrCommands.java

Purpose: registers extended-attribute commands `getfattr` and `setfattr`.

Important APIs and types: nested `GetfattrCommand` and `SetfattrCommand`. Get flags are `-R`, `-n name`, `-d`, and `-e` encoding; set flags are `-n name`, optional `-v value`, or `-x name`.

Control flow: `getfattr` parses optional encoding (`text`, `hex`, `base64`), recursive flag, dump flag, and exactly one path; it requires either named xattr or dump-all. It prints `# file: path`, then either iterates `fs.getXAttrs()` or calls `fs.getXAttr()`, printing attributes with encoded values or just names for zero-length values. `setfattr` requires exactly one of set or remove mode, decodes provided value through `XAttrCodec`, validates one path, then calls `setXAttr()` or `removeXAttr()`.

State and persistence: `getfattr` is read-only. `setfattr` mutates xattr metadata.

Dependencies and integration: uses `XAttrCodec`, Hadoop `StringUtils` option helpers, `Preconditions`, and `HadoopIllegalArgumentException`.

Risks: get dump order follows map iteration order and may be unstable. Values with null are not printed. Recursive get depends on inherited traversal. Value decoding errors propagate from `XAttrCodec`. Namespace and permission rules are delegated to filesystem.

Test signals: cover required option validation, too many/missing path errors, every encoding, empty xattr value, dump-all ordering expectations, recursive get, set with null/decoded values, remove, and mutually exclusive `-n`/`-x`.
