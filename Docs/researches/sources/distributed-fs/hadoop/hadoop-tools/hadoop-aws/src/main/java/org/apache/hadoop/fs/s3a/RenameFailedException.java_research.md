# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/RenameFailedException.java

Purpose: path exception representing a failed S3A rename with a boolean result compatible with `FileSystem.rename()`.

Important APIs/types: extends `PathIOException`; constructors accept string source/destination with cause or error, or `Path` source and optional destination. `getExitCode()` returns the boolean rename result; `withExitCode(boolean)` mutates and returns the exception.

Control flow: constructors set operation to `rename` and target path to destination when available. Callers can throw the exception or inspect/propagate its exit code.

State and persistence behavior: mutable `exitCode` defaults false; path/target/operation stored through `PathIOException`.

Dependencies and integration points: used by S3A rename implementation, which must bridge exception-rich failures and Hadoop's boolean rename contract.

Risks: mutable exit code can be overlooked; default false is conservative. Destination may be null in one constructor.

Test signals: rename tests should assert source, target path, operation, cause/message, default false, and `withExitCode(true)` chaining behavior.
