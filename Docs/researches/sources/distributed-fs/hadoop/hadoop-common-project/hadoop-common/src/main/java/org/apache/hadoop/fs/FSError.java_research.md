## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSError.java

Purpose: `FSError` is a public stable `Error` subtype used for unexpected filesystem failures presumed to reflect serious native disk errors rather than normal recoverable IOExceptions.

Important APIs and types: it extends `Error`, declares `serialVersionUID = 1L`, and has a package-private constructor accepting a `Throwable` cause.

Control flow, state, and persistence: no custom control flow exists. The only state is the inherited cause chain. The package-private constructor restricts creation to Hadoop filesystem package code.

Dependencies and integration: local/native filesystem implementations can wrap severe lower-level failures in `FSError` to signal unrecoverable conditions. Since it is an `Error`, most application code will not catch it.

Risks and test signals: the main risk is overuse for recoverable IO paths, which would bypass normal retry/error handling. Tests should verify cause preservation and that only intended package-level code paths throw it for serious disk-like failures.
