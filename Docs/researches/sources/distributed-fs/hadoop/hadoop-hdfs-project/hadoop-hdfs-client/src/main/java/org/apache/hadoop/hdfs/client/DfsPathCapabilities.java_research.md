# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/DfsPathCapabilities.java

Purpose: `DfsPathCapabilities` provides the shared implementation of `hasPathCapability` for DFS and WebHDFS clients. It maps standardized Hadoop capability strings to HDFS-supported booleans or indicates that the caller should defer to a superclass.

Important APIs/types/functions: `hasPathCapability(Path path, String capability)` validates arguments through `PathCapabilitiesSupport.validatePathCapabilityArgs` and returns `Optional<Boolean>`.

Control flow: a switch returns `Optional.of(true)` for HDFS capabilities including ACLs, append, checksums, concat, corrupt block listing, multipart uploader, path handles, permissions, snapshots, storage policy, xattrs, truncate, and EC policy open-file option. For symlinks it returns `Optional.of(FileSystem.areSymlinksEnabled())`. Unknown capabilities return `Optional.empty()`.

State and persistence behavior: stateless final utility class with private constructor. It performs no I/O and persists no state.

Dependencies and integration points: uses `CommonPathCapabilities`, `Options.OpenFileOptions`, `FileSystem`, `Path`, and the capability validation helper. It is called by DFS-family filesystem implementations to keep capability reporting consistent.

Risks: returning true is a contract to higher layers; if a DFS variant does not support one listed capability, it must override or avoid using this helper. Tests should cover all listed capability constants, symlink enabled/disabled behavior, validation failures for null/empty inputs, and `Optional.empty()` fallback for unknown strings.
