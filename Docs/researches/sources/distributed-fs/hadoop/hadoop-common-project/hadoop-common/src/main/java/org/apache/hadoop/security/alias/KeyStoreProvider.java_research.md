# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/KeyStoreProvider.java

Purpose: abstract filesystem-backed keystore provider for credential stores located on any Hadoop `FileSystem`.

Important APIs/types/functions: extends `AbstractJavaKeyStoreProvider`; fields `FileSystem fs` and `FsPermission permissions`; implements output/input/existence/permission hooks and filesystem initialization.

Control flow: `initFileSystem` delegates URI unnesting to base class then obtains the target path's Hadoop filesystem. Existing keystores stash current `FsPermission`; new stores use requested permissions. `getOutputStreamForKeystore` calls `FileSystem.create(fs, path, permissions)` and `flush` in the base class writes the keystore through that stream.

State/persistence: stores filesystem handle and permissions. Persistent state is the keystore file on the Hadoop filesystem.

Dependencies/integration: Hadoop `FileSystem`, `FSDataOutputStream`, `FileStatus`, `FsPermission`, and concrete scheme providers (`jceks`, `bcfks`).

Risks: `FileSystem.create` overwrite behavior and permission support depend on filesystem implementation; remote filesystems may not enforce POSIX-like permissions; stashed permissions are only as accurate as `getFileStatus`. Test signals include local and remote FS paths, existing permission preservation, new `600` permissions, missing parent/error propagation, and flush overwrite behavior.
