## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/StoragePolicyAdmin.java

Purpose: `StoragePolicyAdmin` is the `hdfs storagepolicies` command implementation. It extends `Configured` and implements `Tool`, dispatching dash-prefixed subcommands through `AdminHelper.Command` instances. The user-facing operations are listing all block storage policies, getting the policy for one path, setting a policy, unsetting a policy, and scheduling `satisfyStoragePolicy`.

Important APIs and control flow: `main` runs the tool with a fresh `Configuration`; `run` validates a subcommand, strips it from the argument list, and delegates to one of the private command classes. `ListStoragePoliciesCommand` calls `FileSystem.get(conf).getAllStoragePolicies()`. `GetStoragePolicyCommand` resolves a path-specific filesystem, obtains `FileStatus`, checks for `HdfsFileStatus`, maps the storage policy id to a `BlockStoragePolicy`, and reports unsupported filesystems. `SetStoragePolicyCommand`, `UnsetStoragePolicyCommand`, and `SatisfyStoragePolicyCommand` call the corresponding `FileSystem` APIs.

State, persistence, and dependencies: the class itself is stateless; persistence happens only through HDFS NameNode RPCs behind `FileSystem`. Dependencies include `BlockStoragePolicySpi`, HDFS protocol types, `Path`, `FileStatus`, `TableListing`, and `StringUtils` option parsing.

Integration points: this is a command-line adapter over HDFS storage-policy APIs and follows the same `AdminHelper` conventions as other HDFS admin tools. Exit codes distinguish usage errors (`1`) from remote/API failures (`2`) and command-dispatch exceptions (`-1`).

Risks and test signals: tests should cover missing options, non-HDFS paths, nonexistent paths, unspecified policies, and each RPC-backed command. A key compatibility risk is assuming policy ids from `HdfsFileStatus` can be resolved by scanning `fs.getAllStoragePolicies()`; unsupported or proxy filesystems should produce the documented error path.
