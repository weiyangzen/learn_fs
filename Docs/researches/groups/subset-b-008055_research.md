# subset-b-008055 Research Group

Generated for work item `subset-b-008055` on 2026-06-17. Each file section preserves the original source path and is delimited for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/UpdateBucketHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/UpdateBucketHandler.java

## Purpose
Picocli/Ozone shell component that updates bucket ownership/versioning attributes. This research is based on a complete read of the 60-line source file.

## Important APIs and Types
Types: `UpdateBucketHandler`. Important methods: `execute`. CLI options/fields: `ownerName` (--user/-u). Ozone/client calls observed: `getVolume`, `getBucket`, `setOwner`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `setOwner`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on volume metadata/quota/ownership; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.bucket` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/UpdateBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell.bucket`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.bucket` integrates with sibling shell commands through picocli subcommands and shared handler/address classes.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/common/VolumeBucketHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/common/VolumeBucketHandler.java

## Purpose
Ozone shell support type `for` for for behavior. This research is based on a complete read of the 38-line source file.

## Important APIs and Types
Types: `for`, `VolumeBucketHandler`. Important methods: `getAddress`. Mixins: `address`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.common` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/common/VolumeBucketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/common/VolumeBucketUri.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/common/VolumeBucketUri.java

## Purpose
Ozone shell support type `VolumeBucketUri` for volumebucket uri behavior. This research is based on a complete read of the 50-line source file.

## Important APIs and Types
Types: `VolumeBucketUri`. Important methods: `getValue`, `convert`. CLI parameters: `value`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.common` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/common/VolumeBucketUri.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/common/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/common/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell.common`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.common` integrates with sibling shell commands through picocli subcommands and shared handler/address classes.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/common/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/AddAclKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/AddAclKeyHandler.java

## Purpose
Picocli/Ozone shell component that adds ACL entries. This research is based on a complete read of the 52-line source file.

## Important APIs and Types
Types: `AddAclKeyHandler`. Important methods: `getAddress`, `execute`. Mixins: `address`, `acls`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/AddAclKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/CatKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/CatKeyHandler.java

## Purpose
Picocli/Ozone shell component that streams key bytes to stdout. This research is based on a complete read of the 51-line source file.

## Important APIs and Types
Types: `CatKeyHandler`. Important methods: `execute`. Ozone/client calls observed: `getVolume`, `getBucket`, `readKey`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `readKey`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/CatKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/ChecksumKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/ChecksumKeyHandler.java

## Purpose
Picocli/Ozone shell component that retrieves and prints key checksum data. This research is based on a complete read of the 99-line source file.

## Important APIs and Types
Types: `ChecksumKeyHandler`, `to`, `ChecksumInfo`. Important methods: `execute`, `getFileChecksum`. CLI options/fields: `ChecksumInfo` (-c/--combine-mode). Ozone/client calls observed: `getVolume`, `getBucket`, `getKey`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `getKey`.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Hadoop filesystem/path utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
Covered by `TestChecksumKeyHandler` for checksum output/parsing behavior. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/ChecksumKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/CopyKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/CopyKeyHandler.java

## Purpose
Picocli/Ozone shell component that copies a key between bucket paths. This research is based on a complete read of the 98-line source file.

## Important APIs and Types
Types: `CopyKeyHandler`. Important methods: `execute`. CLI parameters: `fromKey`, `toKey`. Mixins: `replication`. Ozone/client calls observed: `getVolume`, `getBucket`, `createKey`, `readKey`, `getKey`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `createKey`, `readKey`, `getKey`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on key namespace and key data; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/CopyKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/DeleteKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/DeleteKeyHandler.java

## Purpose
Picocli/Ozone shell component that deletes a key and handles FSO trash behavior. This research is based on a complete read of the 166-line source file.

## Important APIs and Types
Types: `DeleteKeyHandler`, `to`. Important methods: `execute`, `deleteFSOKey`, `isKeyExist`. Ozone/client calls observed: `getVolume`, `getBucket`, `getKey`, `deleteKey`, `renameKey`, `listStatus`, `createDirectory`, `getFileStatus`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `getKey`, `deleteKey`, `renameKey`, `listStatus`, `createDirectory`, `getFileStatus`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on key namespace and key data; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Hadoop filesystem/path utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials. FSO trash handling has path-sensitive behavior around existing trash entries, non-empty directories, and reserved snapshot words.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Destructive and recursive flows need layout-specific integration tests for OBJECT_STORE, LEGACY, and FSO buckets.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/DeleteKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/GetAclKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/GetAclKeyHandler.java

## Purpose
Picocli/Ozone shell component that reads ACL entries. This research is based on a complete read of the 41-line source file.

## Important APIs and Types
Types: `GetAclKeyHandler`. Important methods: `getAddress`. Mixins: `address`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/GetAclKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/GetKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/GetKeyHandler.java

## Purpose
Picocli/Ozone shell component that downloads a key to the local filesystem. This research is based on a complete read of the 95-line source file.

## Important APIs and Types
Types: `GetKeyHandler`. Important methods: `execute`. CLI options/fields: `force` (-f/--force/false). CLI parameters: `fileName`. Ozone/client calls observed: `getVolume`, `getBucket`, `readKey`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `readKey`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/GetKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/InfoKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/InfoKeyHandler.java

## Purpose
Picocli/Ozone shell component that prints key metadata. This research is based on a complete read of the 56-line source file.

## Important APIs and Types
Types: `InfoKeyHandler`. Important methods: `execute`. Ozone/client calls observed: `getVolume`, `getBucket`, `getKey`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `getKey`.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/InfoKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/KeyCommands.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/KeyCommands.java

## Purpose
Picocli/Ozone shell component for `key`: Key specific operations. This research is based on a complete read of the 49-line source file.

## Important APIs and Types
Types: `KeyCommands`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; HDDS config/replication helpers.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/KeyCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/KeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/KeyHandler.java

## Purpose
Ozone shell support type `for` for for behavior. This research is based on a complete read of the 38-line source file.

## Important APIs and Types
Types: `for`, `KeyHandler`. Important methods: `getAddress`. Mixins: `address`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/KeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/KeyUri.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/KeyUri.java

## Purpose
Ozone shell support type `KeyUri` for key uri behavior. This research is based on a complete read of the 49-line source file.

## Important APIs and Types
Types: `KeyUri`. Important methods: `getValue`, `convert`. CLI parameters: `value`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/KeyUri.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/ListKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/ListKeyHandler.java

## Purpose
Picocli/Ozone shell component that lists keys with pagination/filtering. This research is based on a complete read of the 146-line source file.

## Important APIs and Types
Types: `ListKeyHandler`. Important methods: `execute`, `listKeysInsideBucket`, `listKeysInsideVolume`. Mixins: `listOptions`, `prefixFilter`. Ozone/client calls observed: `getVolume`, `getBucket`, `listKeys`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `listKeys`. Iterator loops page through server-side listings and print or batch results incrementally. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/ListKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/PutKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/PutKeyHandler.java

## Purpose
Picocli/Ozone shell component that uploads a local file as a key. This research is based on a complete read of the 172-line source file.

## Important APIs and Types
Types: `PutKeyHandler`. Important methods: `execute`, `async`, `createOrReplaceKey`, `stream`. CLI options/fields: `stream` (--stream), `expectedGeneration` (--expectedGeneration). CLI parameters: `fileName`. Mixins: `replication`. Ozone/client calls observed: `getVolume`, `getBucket`, `createKey`, `rewriteKey`, `createStreamKey`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `createKey`, `rewriteKey`, `createStreamKey`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on key namespace and key data; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Upload path depends on replication resolution, chunk size, expected generation, and streaming incompatibility with EC replication. Validation exceptions are part of user-visible CLI behavior and should remain stable.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/PutKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/RemoveAclKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/RemoveAclKeyHandler.java

## Purpose
Picocli/Ozone shell component that removes ACL entries. This research is based on a complete read of the 52-line source file.

## Important APIs and Types
Types: `RemoveAclKeyHandler`. Important methods: `getAddress`, `execute`. Mixins: `address`, `acls`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/RemoveAclKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/RenameKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/RenameKeyHandler.java

## Purpose
Picocli/Ozone shell component that renames a key. This research is based on a complete read of the 60-line source file.

## Important APIs and Types
Types: `RenameKeyHandler`. Important methods: `execute`. CLI parameters: `fromKey`, `toKey`. Ozone/client calls observed: `getVolume`, `getBucket`, `renameKey`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `renameKey`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on key namespace and key data; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/RenameKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/RewriteKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/RewriteKeyHandler.java

## Purpose
Picocli/Ozone shell component that rewrites a key generation. This research is based on a complete read of the 70-line source file.

## Important APIs and Types
Types: `RewriteKeyHandler`. Important methods: `execute`. Mixins: `replication`. Ozone/client calls observed: `getVolume`, `getBucket`, `rewriteKey`, `readKey`, `getKey`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `rewriteKey`, `readKey`, `getKey`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on key namespace and key data; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/RewriteKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/SetAclKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/SetAclKeyHandler.java

## Purpose
Picocli/Ozone shell component that replaces ACL entries. This research is based on a complete read of the 53-line source file.

## Important APIs and Types
Types: `SetAclKeyHandler`. Important methods: `getAddress`, `execute`. Mixins: `address`, `acls`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/SetAclKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell.keys`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell` integrates with sibling shell commands through picocli subcommands and shared handler/address classes.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/AddAclPrefixHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/AddAclPrefixHandler.java

## Purpose
Picocli/Ozone shell component that adds ACL entries. This research is based on a complete read of the 52-line source file.

## Important APIs and Types
Types: `AddAclPrefixHandler`. Important methods: `getAddress`, `execute`. Mixins: `address`, `acls`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.prefix` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/AddAclPrefixHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/GetAclPrefixHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/GetAclPrefixHandler.java

## Purpose
Picocli/Ozone shell component that reads ACL entries. This research is based on a complete read of the 41-line source file.

## Important APIs and Types
Types: `GetAclPrefixHandler`. Important methods: `getAddress`. Mixins: `address`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.prefix` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/GetAclPrefixHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/PrefixCommands.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/PrefixCommands.java

## Purpose
Picocli/Ozone shell component for `prefix`: Prefix specific operations. This research is based on a complete read of the 39-line source file.

## Important APIs and Types
Types: `PrefixCommands`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.prefix` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; HDDS config/replication helpers.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/PrefixCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/PrefixUri.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/PrefixUri.java

## Purpose
Ozone shell support type `PrefixUri` for prefix uri behavior. This research is based on a complete read of the 49-line source file.

## Important APIs and Types
Types: `PrefixUri`. Important methods: `getValue`, `convert`. CLI parameters: `value`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.prefix` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/PrefixUri.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/RemoveAclPrefixHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/RemoveAclPrefixHandler.java

## Purpose
Picocli/Ozone shell component that removes ACL entries. This research is based on a complete read of the 52-line source file.

## Important APIs and Types
Types: `RemoveAclPrefixHandler`. Important methods: `getAddress`, `execute`. Mixins: `address`, `acls`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.prefix` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/RemoveAclPrefixHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/SetAclPrefixHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/SetAclPrefixHandler.java

## Purpose
Picocli/Ozone shell component that replaces ACL entries. This research is based on a complete read of the 53-line source file.

## Important APIs and Types
Types: `SetAclPrefixHandler`. Important methods: `getAddress`, `execute`. Mixins: `address`, `acls`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.prefix` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/SetAclPrefixHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell.prefix`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.prefix` integrates with sibling shell commands through picocli subcommands and shared handler/address classes.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/prefix/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/GetS3SecretHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/GetS3SecretHandler.java

## Purpose
Picocli/Ozone shell component that gets or creates an S3 secret. This research is based on a complete read of the 68-line source file.

## Important APIs and Types
Types: `GetS3SecretHandler`. Important methods: `isApplicable`, `execute`. CLI options/fields: `username` (-u), `export` (-e). Ozone/client calls observed: `getS3Secret`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getS3Secret`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on S3 secret material or secret metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.s3` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Secret output must avoid accidental logging beyond the intended command output channel.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/GetS3SecretHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/RevokeS3SecretHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/RevokeS3SecretHandler.java

## Purpose
Picocli/Ozone shell component that revokes an S3 secret. This research is based on a complete read of the 76-line source file.

## Important APIs and Types
Types: `RevokeS3SecretHandler`. Important methods: `isApplicable`, `execute`. CLI options/fields: `username` (-u), `yes` (-y). Ozone/client calls observed: `revokeS3Secret`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `revokeS3Secret`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on S3 secret material or secret metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.s3` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials. Secret output must avoid accidental logging beyond the intended command output channel.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/RevokeS3SecretHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/S3Handler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/S3Handler.java

## Purpose
Ozone shell support type `for` for for behavior. This research is based on a complete read of the 54-line source file.

## Important APIs and Types
Types: `for`, `S3Handler`. Important methods: `getOmServiceID`, `getAddress`, `createClient`. CLI options/fields: `omServiceID` (--om-service-id).

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.s3` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/S3Handler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/S3Shell.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/S3Shell.java

## Purpose
Picocli/Ozone shell component for `ozone s3`: Shell for S3 specific operations. This research is based on a complete read of the 39-line source file.

## Important APIs and Types
Types: `S3Shell`. Important methods: `main`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.s3` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/S3Shell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/SetS3SecretHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/SetS3SecretHandler.java

## Purpose
Picocli/Ozone shell component that sets an S3 secret. This research is based on a complete read of the 75-line source file.

## Important APIs and Types
Types: `SetS3SecretHandler`. Important methods: `isApplicable`, `execute`. CLI options/fields: `username` (-u), `secretKey` (-s/--secret/--secretKey), `export` (-e). Ozone/client calls observed: `setS3Secret`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `setS3Secret`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on S3 secret material or secret metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.s3` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Secret output must avoid accidental logging beyond the intended command output channel.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/SetS3SecretHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell.s3`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.s3` integrates with sibling shell commands through picocli subcommands and shared handler/address classes.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/s3/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/BucketSnapshotHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/BucketSnapshotHandler.java

## Purpose
Ozone shell support type `for` for for behavior. This research is based on a complete read of the 37-line source file.

## Important APIs and Types
Types: `for`, `BucketSnapshotHandler`. Important methods: `getAddress`. Mixins: `address`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/BucketSnapshotHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/CreateSnapshotHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/CreateSnapshotHandler.java

## Purpose
Picocli/Ozone shell component that creates a bucket snapshot. This research is based on a complete read of the 62-line source file.

## Important APIs and Types
Types: `CreateSnapshotHandler`. Important methods: `getAddress`, `execute`. CLI parameters: `snapshotName`. Mixins: `snapshotPath`. Ozone/client calls observed: `createSnapshot`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `createSnapshot`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on snapshot metadata/diff jobs; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Validation exceptions are part of user-visible CLI behavior and should remain stable.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/CreateSnapshotHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/DeleteSnapshotHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/DeleteSnapshotHandler.java

## Purpose
Picocli/Ozone shell component that deletes a bucket snapshot. This research is based on a complete read of the 61-line source file.

## Important APIs and Types
Types: `DeleteSnapshotHandler`. Important methods: `getAddress`, `execute`. CLI parameters: `snapshotName`. Mixins: `snapshotPath`. Ozone/client calls observed: `deleteSnapshot`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `deleteSnapshot`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on snapshot metadata/diff jobs; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/DeleteSnapshotHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/InfoSnapshotHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/InfoSnapshotHandler.java

## Purpose
Picocli/Ozone shell component that prints snapshot metadata. This research is based on a complete read of the 63-line source file.

## Important APIs and Types
Types: `InfoSnapshotHandler`. Important methods: `getAddress`, `execute`. CLI parameters: `snapshotName`. Mixins: `snapshotPath`. Ozone/client calls observed: `getSnapshotInfo`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getSnapshotInfo`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/InfoSnapshotHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/ListSnapshotDiffHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/ListSnapshotDiffHandler.java

## Purpose
Picocli/Ozone shell component that lists snapshot diff jobs. This research is based on a complete read of the 75-line source file.

## Important APIs and Types
Types: `ListSnapshotDiffHandler`. Important methods: `getAddress`, `execute`. CLI options/fields: `jobStatus` (--job-status/in_progress), `listAllStatus` (--all-status/false). Mixins: `snapshotPath`, `listOptions`. Ozone/client calls observed: `listSnapshotDiffJobs`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `listSnapshotDiffJobs`. Iterator loops page through server-side listings and print or batch results incrementally. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Snapshot diff has compatibility fallback and pagination/token behavior; regressions can duplicate, omit, or misformat diff entries.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/ListSnapshotDiffHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/ListSnapshotHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/ListSnapshotHandler.java

## Purpose
Picocli/Ozone shell component that lists snapshots. This research is based on a complete read of the 70-line source file.

## Important APIs and Types
Types: `ListSnapshotHandler`. Important methods: `getAddress`, `execute`. Mixins: `snapshotPath`, `listOptions`, `prefixFilter`. Ozone/client calls observed: `listSnapshot`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `listSnapshot`. Iterator loops page through server-side listings and print or batch results incrementally. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/ListSnapshotHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/RenameSnapshotHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/RenameSnapshotHandler.java

## Purpose
Picocli/Ozone shell component that renames a snapshot. This research is based on a complete read of the 64-line source file.

## Important APIs and Types
Types: `RenameSnapshotHandler`. Important methods: `getAddress`, `execute`. CLI parameters: `snapshotOldName`, `snapshotNewName`. Mixins: `snapshotPath`. Ozone/client calls observed: `renameSnapshot`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `renameSnapshot`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on snapshot metadata/diff jobs; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Validation exceptions are part of user-visible CLI behavior and should remain stable.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/RenameSnapshotHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/SnapshotCommands.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/SnapshotCommands.java

## Purpose
Picocli/Ozone shell component for `snapshot`: Snapshot specific operations. This research is based on a complete read of the 42-line source file.

## Important APIs and Types
Types: `SnapshotCommands`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; HDDS config/replication helpers.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/SnapshotCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/SnapshotDiffHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/SnapshotDiffHandler.java

## Purpose
Picocli/Ozone shell component that submits, cancels, or fetches snapshot diffs. This research is based on a complete read of the 223-line source file.

## Important APIs and Types
Types: `SnapshotDiffHandler`. Important methods: `getAddress`, `execute`, `submitSnapshotDiff`, `getSnapshotDiff`, `cancelSnapshotDiff`, `getJsonObject`, `getJsonObject`, `getJsonObject`, `getPathString`. CLI options/fields: `token` (-t/--token), `pageSize` (-p/--page-size/1000), `forceFullDiff` (--ffd/--force-full-diff), `cancel` (-c/--cancel/false), `getReport` (-r/--get-report/false), `diffDisableNativeLibs` (--dnld/--disable-native-libs-diff), `json` (--json/false). CLI parameters: `fromSnapshot`, `toSnapshot`. Mixins: `snapshotPath`. Ozone/client calls observed: `snapshotDiff`, `submitSnapshotDiff`, `cancelSnapshotDiff`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `snapshotDiff`, `submitSnapshotDiff`, `cancelSnapshotDiff`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on snapshot metadata/diff jobs; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Hadoop filesystem/path utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Snapshot diff has compatibility fallback and pagination/token behavior; regressions can duplicate, omit, or misformat diff entries. Validation exceptions are part of user-visible CLI behavior and should remain stable.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/SnapshotDiffHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/SnapshotUri.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/SnapshotUri.java

## Purpose
Ozone shell support type `SnapshotUri` for snapshot uri behavior. This research is based on a complete read of the 48-line source file.

## Important APIs and Types
Types: `SnapshotUri`. Important methods: `getValue`, `convert`. CLI parameters: `value`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/SnapshotUri.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell.snapshot`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/GetUserInfoHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/GetUserInfoHandler.java

## Purpose
Picocli/Ozone shell component that prints tenant/user access information. This research is based on a complete read of the 92-line source file.

## Important APIs and Types
Types: `GetUserInfoHandler`. Important methods: `execute`. CLI options/fields: `printJson` (--json/-j). CLI parameters: `userPrincipal`. Ozone/client calls observed: `tenantGetUserInfo`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `tenantGetUserInfo`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers; Jackson JSON serialization. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/GetUserInfoHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantAssignAdminHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantAssignAdminHandler.java

## Purpose
Picocli/Ozone shell component that assigns a tenant admin. This research is based on a complete read of the 67-line source file.

## Important APIs and Types
Types: `TenantAssignAdminHandler`. Important methods: `execute`. CLI options/fields: `tenantId` (-t/--tenant), `delegated` (-d/--delegated/false). CLI parameters: `accessId`. Ozone/client calls observed: `tenantAssignAdmin`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `tenantAssignAdmin`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on tenant/account/link metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers; Jackson JSON serialization. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantAssignAdminHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantAssignUserAccessIdHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantAssignUserAccessIdHandler.java

## Purpose
Picocli/Ozone shell component that assigns a tenant access ID. This research is based on a complete read of the 83-line source file.

## Important APIs and Types
Types: `TenantAssignUserAccessIdHandler`. Important methods: `getDefaultAccessId`, `execute`. CLI options/fields: `tenantId` (-t/--tenant). CLI parameters: `userPrincipal`. Ozone/client calls observed: `tenantAssignUserAccessId`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `tenantAssignUserAccessId`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on tenant/account/link metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantAssignUserAccessIdHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantBucketLinkHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantBucketLinkHandler.java

## Purpose
Picocli/Ozone shell component that links a bucket into a tenant volume. This research is based on a complete read of the 74-line source file.

## Important APIs and Types
Types: `TenantBucketLinkHandler`. Important methods: `execute`. CLI parameters: `source`, `target`. Ozone/client calls observed: `getVolume`, `getBucket`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantBucketLinkHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantCreateHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantCreateHandler.java

## Purpose
Picocli/Ozone shell component that creates a tenant. This research is based on a complete read of the 67-line source file.

## Important APIs and Types
Types: `TenantCreateHandler`. Important methods: `execute`. CLI parameters: `tenantId`. Ozone/client calls observed: `createTenant`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `createTenant`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on tenant/account/link metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers; Jackson JSON serialization. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantCreateHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantDeleteHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantDeleteHandler.java

## Purpose
Picocli/Ozone shell component that deletes a tenant. This research is based on a complete read of the 72-line source file.

## Important APIs and Types
Types: `TenantDeleteHandler`. Important methods: `execute`. CLI parameters: `tenantId`. Ozone/client calls observed: `deleteTenant`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `deleteTenant`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on tenant/account/link metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers; Jackson JSON serialization. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantDeleteHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantGetSecretHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantGetSecretHandler.java

## Purpose
Picocli/Ozone shell component that gets a tenant S3 secret. This research is based on a complete read of the 53-line source file.

## Important APIs and Types
Types: `TenantGetSecretHandler`. Important methods: `execute`. CLI parameters: `accessId`. Ozone/client calls observed: `getS3Secret`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getS3Secret`.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on S3 secret material or secret metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Secret output must avoid accidental logging beyond the intended command output channel.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantGetSecretHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantHandler.java

## Purpose
Ozone shell support type `for` for for behavior. This research is based on a complete read of the 54-line source file.

## Important APIs and Types
Types: `for`, `TenantHandler`. Important methods: `getOmServiceID`, `getAddress`, `createClient`. CLI options/fields: `omServiceID` (--om-service-id).

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantListHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantListHandler.java

## Purpose
Picocli/Ozone shell component that lists tenants. This research is based on a complete read of the 69-line source file.

## Important APIs and Types
Types: `TenantListHandler`. Important methods: `execute`. CLI options/fields: `printJson` (--json/-j). Ozone/client calls observed: `listTenant`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `listTenant`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers; Jackson JSON serialization. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantListHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantListUsersHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantListUsersHandler.java

## Purpose
Picocli/Ozone shell component that lists users in a tenant. This research is based on a complete read of the 78-line source file.

## Important APIs and Types
Types: `TenantListUsersHandler`. Important methods: `execute`. CLI options/fields: `prefix` (--prefix/-p), `printJson` (--json/-j). CLI parameters: `tenantId`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers; Jackson JSON serialization.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantListUsersHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantRevokeAdminHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantRevokeAdminHandler.java

## Purpose
Picocli/Ozone shell component that revokes a tenant admin. This research is based on a complete read of the 60-line source file.

## Important APIs and Types
Types: `TenantRevokeAdminHandler`. Important methods: `execute`. CLI options/fields: `tenantId` (-t/--tenant). CLI parameters: `accessId`. Ozone/client calls observed: `tenantRevokeAdmin`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `tenantRevokeAdmin`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on tenant/account/link metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers; Jackson JSON serialization. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantRevokeAdminHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantRevokeUserAccessIdHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantRevokeUserAccessIdHandler.java

## Purpose
Picocli/Ozone shell component that revokes a tenant access ID. This research is based on a complete read of the 45-line source file.

## Important APIs and Types
Types: `TenantRevokeUserAccessIdHandler`. Important methods: `execute`. CLI parameters: `accessId`. Ozone/client calls observed: `tenantRevokeUserAccessId`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `tenantRevokeUserAccessId`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on tenant/account/link metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantRevokeUserAccessIdHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantSetSecretHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantSetSecretHandler.java

## Purpose
Picocli/Ozone shell component that sets a tenant S3 secret. This research is based on a complete read of the 55-line source file.

## Important APIs and Types
Types: `TenantSetSecretHandler`. Important methods: `execute`. CLI options/fields: `secretKey` (-s/--secret). CLI parameters: `accessId`. Ozone/client calls observed: `setS3Secret`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `setS3Secret`.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on S3 secret material or secret metadata; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Secret output must avoid accidental logging beyond the intended command output channel.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantSetSecretHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantShell.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantShell.java

## Purpose
Picocli/Ozone shell component for `ozone tenant`: Shell for multi-tenant specific operations. This research is based on a complete read of the 41-line source file.

## Important APIs and Types
Types: `TenantShell`. Important methods: `main`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantUserCommands.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantUserCommands.java

## Purpose
Picocli/Ozone shell component for `user`: Tenant user management. This research is based on a complete read of the 43-line source file.

## Important APIs and Types
Types: `TenantUserCommands`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; HDDS config/replication helpers.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
Tenant/S3 secret behavior should be covered by secure integration tests because mocks cannot prove OM authorization semantics.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/TenantUserCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell.tenant`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.tenant` integrates with sibling shell commands through picocli subcommands and shared handler/address classes.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/tenant/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/CancelTokenHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/CancelTokenHandler.java

## Purpose
Picocli/Ozone shell component that cancels a delegation token. This research is based on a complete read of the 39-line source file.

## Important APIs and Types
Types: `CancelTokenHandler`. Important methods: `execute`. Ozone/client calls observed: `cancelDelegationToken`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `cancelDelegationToken`.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on delegation token lifecycle; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.token` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/CancelTokenHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/GetTokenHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/GetTokenHandler.java

## Purpose
Picocli/Ozone shell component that gets a delegation token. This research is based on a complete read of the 86-line source file.

## Important APIs and Types
Types: `GetTokenHandler`. Important methods: `getAddress`, `isApplicable`, `execute`. CLI parameters: `uri`. Mixins: `renewer`, `tokenFile`. Ozone/client calls observed: `getDelegationToken`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getDelegationToken`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on delegation token lifecycle; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.token` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/GetTokenHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/PrintTokenHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/PrintTokenHandler.java

## Purpose
Picocli/Ozone shell component that prints token details. This research is based on a complete read of the 46-line source file.

## Important APIs and Types
Types: `PrintTokenHandler`. Important methods: `call`. Mixins: `tokenFile`.

## Control Flow
Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.token` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/PrintTokenHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/RenewTokenHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/RenewTokenHandler.java

## Purpose
Picocli/Ozone shell component that renews a delegation token. This research is based on a complete read of the 41-line source file.

## Important APIs and Types
Types: `RenewTokenHandler`. Important methods: `execute`. Ozone/client calls observed: `renewDelegationToken`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `renewDelegationToken`.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on delegation token lifecycle; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.token` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/RenewTokenHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/RenewerOption.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/RenewerOption.java

## Purpose
Ozone shell support type `RenewerOption` for reneweroption behavior. This research is based on a complete read of the 42-line source file.

## Important APIs and Types
Types: `RenewerOption`. Important methods: `getValue`. CLI options/fields: `renewer` (--renewer/-r).

## Control Flow
Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.token` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/RenewerOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/TokenCommands.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/TokenCommands.java

## Purpose
Picocli/Ozone shell component for `token`: Token specific operations. This research is based on a complete read of the 39-line source file.

## Important APIs and Types
Types: `TokenCommands`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.token` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; HDDS config/replication helpers.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/TokenCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/TokenHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/TokenHandler.java

## Purpose
Ozone shell support type `TokenHandler` for token behavior. This research is based on a complete read of the 54-line source file.

## Important APIs and Types
Types: `TokenHandler`. Important methods: `isApplicable`, `createClient`. Mixins: `tokenFile`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.token` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/TokenHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/TokenOption.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/TokenOption.java

## Purpose
Ozone shell support type `TokenOption` for tokenoption behavior. This research is based on a complete read of the 84-line source file.

## Important APIs and Types
Types: `TokenOption`. Important methods: `exists`, `decode`, `persistToken`, `getTokenFilePath`. CLI options/fields: `tokenFile` (--token/-t).

## Control Flow
I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.token` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/TokenOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell.token`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.token` integrates with sibling shell commands through picocli subcommands and shared handler/address classes.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/token/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/AddAclVolumeHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/AddAclVolumeHandler.java

## Purpose
Picocli/Ozone shell component that adds ACL entries. This research is based on a complete read of the 52-line source file.

## Important APIs and Types
Types: `AddAclVolumeHandler`. Important methods: `getAddress`, `execute`. Mixins: `address`, `acls`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/AddAclVolumeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/ClearQuotaHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/ClearQuotaHandler.java

## Purpose
Picocli/Ozone shell component that clears quota. This research is based on a complete read of the 60-line source file.

## Important APIs and Types
Types: `ClearQuotaHandler`. Important methods: `execute`. Mixins: `clrSpaceQuota`. Ozone/client calls observed: `getVolume`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/ClearQuotaHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/CreateVolumeHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/CreateVolumeHandler.java

## Purpose
Picocli/Ozone shell component that creates a volume. This research is based on a complete read of the 81-line source file.

## Important APIs and Types
Types: `CreateVolumeHandler`. Important methods: `execute`. CLI options/fields: `ownerName` (--user/-u). Mixins: `quotaOptions`. Ozone/client calls observed: `getVolume`, `createVolume`, `setOwner`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `createVolume`, `setOwner`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on volume metadata/quota/ownership; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/CreateVolumeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/DeleteVolumeHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/DeleteVolumeHandler.java

## Purpose
Picocli/Ozone shell component that deletes a volume, optionally recursively. This research is based on a complete read of the 237-line source file.

## Important APIs and Types
Types: `DeleteVolumeHandler`, `BucketCleaner`. Important methods: `execute`, `deleteVolumeRecursive`, `cleanOBSBucket`, `cleanFSBucket`, `run`, `doCleanBuckets`. CLI options/fields: `bRecursive` (-r), `threadNo` (-t/--threads/--thread), `yes` (-y/--yes). Ozone/client calls observed: `getVolume`, `getBucket`, `deleteKeys`, `listKeys`, `deleteVolume`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `deleteKeys`, `listKeys`, `deleteVolume`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Iterator loops page through server-side listings and print or batch results incrementally. Recursive volume deletion fans bucket cleanup out through a fixed thread pool and shared atomic counters. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on key namespace and key data, volume metadata/quota/ownership; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Hadoop filesystem/path utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials. Recursive deletion combines concurrency, batch deletes, and filesystem deletion for FSO/legacy buckets; interruption and partial failure handling are important.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Destructive and recursive flows need layout-specific integration tests for OBJECT_STORE, LEGACY, and FSO buckets.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/DeleteVolumeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/GetAclVolumeHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/GetAclVolumeHandler.java

## Purpose
Picocli/Ozone shell component that reads ACL entries. This research is based on a complete read of the 41-line source file.

## Important APIs and Types
Types: `GetAclVolumeHandler`. Important methods: `getAddress`. Mixins: `address`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/GetAclVolumeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/InfoVolumeHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/InfoVolumeHandler.java

## Purpose
Picocli/Ozone shell component that prints volume metadata. This research is based on a complete read of the 43-line source file.

## Important APIs and Types
Types: `InfoVolumeHandler`. Important methods: `execute`. Ozone/client calls observed: `getVolume`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/InfoVolumeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/ListVolumeHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/ListVolumeHandler.java

## Purpose
Picocli/Ozone shell component that lists volumes. This research is based on a complete read of the 92-line source file.

## Important APIs and Types
Types: `ListVolumeHandler`. Important methods: `getAddress`, `execute`. CLI options/fields: `userName` (--user/-u). CLI parameters: `uri`. Mixins: `listOptions`, `prefixFilter`. Ozone/client calls observed: `listVolumes`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `listVolumes`. Iterator loops page through server-side listings and print or batch results incrementally. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/ListVolumeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/RemoveAclVolumeHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/RemoveAclVolumeHandler.java

## Purpose
Picocli/Ozone shell component that removes ACL entries. This research is based on a complete read of the 52-line source file.

## Important APIs and Types
Types: `RemoveAclVolumeHandler`. Important methods: `getAddress`, `execute`. Mixins: `address`, `acls`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/RemoveAclVolumeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/SetAclVolumeHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/SetAclVolumeHandler.java

## Purpose
Picocli/Ozone shell component that replaces ACL entries. This research is based on a complete read of the 53-line source file.

## Important APIs and Types
Types: `SetAclVolumeHandler`. Important methods: `getAddress`, `execute`. Mixins: `address`, `acls`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
ACL output behavior is represented by `TestGetAclHandler`; mutation handlers need complementary integration tests. URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/SetAclVolumeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/SetQuotaHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/SetQuotaHandler.java

## Purpose
Picocli/Ozone shell component that sets quota. This research is based on a complete read of the 79-line source file.

## Important APIs and Types
Types: `SetQuotaHandler`. Important methods: `execute`. Mixins: `quotaOptions`. Ozone/client calls observed: `getVolume`, `setQuota`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `setQuota`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/SetQuotaHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/UpdateVolumeHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/UpdateVolumeHandler.java

## Purpose
Picocli/Ozone shell component that updates volume ownership/quota attributes. This research is based on a complete read of the 57-line source file.

## Important APIs and Types
Types: `UpdateVolumeHandler`. Important methods: `execute`. CLI options/fields: `ownerName` (--user). Ozone/client calls observed: `getVolume`, `setOwner`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `setOwner`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on volume metadata/quota/ownership; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/UpdateVolumeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/VolumeCommands.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/VolumeCommands.java

## Purpose
Picocli/Ozone shell component for `volume`: Volume specific operations. This research is based on a complete read of the 47-line source file.

## Important APIs and Types
Types: `VolumeCommands`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; HDDS config/replication helpers.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/VolumeCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/VolumeHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/VolumeHandler.java

## Purpose
Ozone shell support type `for` for for behavior. This research is based on a complete read of the 38-line source file.

## Important APIs and Types
Types: `for`, `VolumeHandler`. Important methods: `getAddress`. Mixins: `address`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/VolumeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/VolumeUri.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/VolumeUri.java

## Purpose
Ozone shell support type `VolumeUri` for volume uri behavior. This research is based on a complete read of the 49-line source file.

## Important APIs and Types
Types: `VolumeUri`. Important methods: `getValue`, `convert`. CLI parameters: `value`.

## Control Flow
Control flow is minimal: helper/accessor methods return parsed values or construct command objects for the surrounding shell framework.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/VolumeUri.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell.volume`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneAddress.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneAddress.java

## Purpose
JUnit test coverage for `TestOzoneAddress` focused on Ozone shell address/client behavior or command output semantics. This research is based on a complete read of the 136-line source file.

## Important APIs and Types
Types: `TestOzoneAddress`. Important methods: `data`, `checkRootUrlType`, `checkVolumeUrlType`, `checkBucketUrlType`, `checkKeyUrlType`, `checkPrefixUrlType`, `checkSnapshotUrlType`.

## Control Flow
Each `@Test` constructs mock or concrete inputs, invokes the shell/client path under test, then asserts parsed addresses, generated clients, checksums, ACL JSON/string output, or error behavior. Test methods: data, checkRootUrlType, checkVolumeUrlType, checkBucketUrlType, checkKeyUrlType, checkPrefixUrlType, checkSnapshotUrlType.

## State and Persistence
Test state is local to each test method, using mocks, temporary streams, and captured stdout/stderr; it should not mutate a real Ozone deployment.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: Ozone client object-store API; JUnit tests; AssertJ assertions. Test integration uses JUnit, Mockito, command-line parsing, and captured streams rather than a live OM unless explicitly configured by the test.

## Risks and Edge Cases
Tests rely on command-line parsing and mock behavior matching production APIs; server-side integration remains covered elsewhere.

## Test Signals
This is direct test code using assertEquals, assertTrue, assertThrows, assertThat to exercise the behavior described above.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneAddress.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneAddressClientCreation.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneAddressClientCreation.java

## Purpose
JUnit test coverage for `TestOzoneAddressClientCreation` focused on Ozone shell address/client behavior or command output semantics. This research is based on a complete read of the 217-line source file.

## Important APIs and Types
Types: `TestOzoneAddressClientCreation`, `TestableOzoneAddress`. Important methods: `implicitNonHA`, `implicitHAOneServiceId`, `implicitHaMultipleServiceId`, `implicitHaMultipleServiceIdWithDefaultServiceId`, `implicitHaMultipleServiceIdWithDefaultServiceIdForS3`, `explicitHaMultipleServiceId`, `explicitNonHAHostPort`, `explicitHAHostPortWithServiceId`, `explicitAHostPortWithServiceIds`, `explicitNonHAHost`, `explicitHAHostPort`, `explicitWrongScheme`.

## Control Flow
Each `@Test` constructs mock or concrete inputs, invokes the shell/client path under test, then asserts parsed addresses, generated clients, checksums, ACL JSON/string output, or error behavior. Test methods: implicitNonHA, implicitHAOneServiceId, implicitHaMultipleServiceId, implicitHaMultipleServiceIdWithDefaultServiceId, implicitHaMultipleServiceIdWithDefaultServiceIdForS3, explicitHaMultipleServiceId, explicitNonHAHostPort, explicitHAHostPortWithServiceId.

## State and Persistence
Test state is local to each test method, using mocks, temporary streams, and captured stdout/stderr; it should not mutate a real Ozone deployment.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: Ozone client object-store API; HDDS config/replication helpers; JUnit tests. Test integration uses JUnit, Mockito, command-line parsing, and captured streams rather than a live OM unless explicitly configured by the test.

## Risks and Edge Cases
Tests rely on command-line parsing and mock behavior matching production APIs; server-side integration remains covered elsewhere.

## Test Signals
This is direct test code using assertEquals, assertTrue, assertThrows to exercise the behavior described above.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneAddressClientCreation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/acl/TestGetAclHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/acl/TestGetAclHandler.java

## Purpose
JUnit test coverage for `TestGetAclHandler` focused on Ozone shell address/client behavior or command output semantics. This research is based on a complete read of the 226-line source file.

## Important APIs and Types
Types: `TestGetAclHandler`, `TestableGetAclBucketHandler`. Important methods: `publicExecute`, `setup`, `tearDown`, `testGetAclAsJson`, `testGetAclAsStringWithAccessScope`, `testGetAclAsStringWithDefaultScope`, `testGetAclAsStringMixedScopes`. Ozone/client calls observed: `getAcl`.

## Control Flow
Each `@Test` constructs mock or concrete inputs, invokes the shell/client path under test, then asserts parsed addresses, generated clients, checksums, ACL JSON/string output, or error behavior. Test methods: publicExecute, setup, tearDown, testGetAclAsJson, testGetAclAsStringWithAccessScope, testGetAclAsStringWithDefaultScope, testGetAclAsStringMixedScopes.

## State and Persistence
Test state is local to each test method, using mocks, temporary streams, and captured stdout/stderr; it should not mutate a real Ozone deployment.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.acl` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Ozone ACL object model; Jackson JSON serialization. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior. Test integration uses JUnit, Mockito, command-line parsing, and captured streams rather than a live OM unless explicitly configured by the test.

## Risks and Edge Cases
Tests rely on command-line parsing and mock behavior matching production APIs; server-side integration remains covered elsewhere.

## Test Signals
This is direct test code using assertEquals, assertTrue, when to exercise the behavior described above.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/acl/TestGetAclHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/keys/TestChecksumKeyHandler.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/keys/TestChecksumKeyHandler.java

## Purpose
JUnit test coverage for `TestChecksumKeyHandler` focused on Ozone shell address/client behavior or command output semantics. This research is based on a complete read of the 119-line source file.

## Important APIs and Types
Types: `TestChecksumKeyHandler`. Important methods: `setup`, `getFileChecksum`, `tearDown`, `testChecksumKeyHandler`. Ozone/client calls observed: `getVolume`, `getBucket`, `getKey`.

## Control Flow
Each `@Test` constructs mock or concrete inputs, invokes the shell/client path under test, then asserts parsed addresses, generated clients, checksums, ACL JSON/string output, or error behavior. Test methods: setup, getFileChecksum, tearDown, testChecksumKeyHandler.

## State and Persistence
Test state is local to each test method, using mocks, temporary streams, and captured stdout/stderr; it should not mutate a real Ozone deployment.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: Ozone client object-store API; shared shell handler/address utilities; Hadoop filesystem/path utilities; Jackson JSON serialization; JUnit tests. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior. Test integration uses JUnit, Mockito, command-line parsing, and captured streams rather than a live OM unless explicitly configured by the test.

## Risks and Edge Cases
Tests rely on command-line parsing and mock behavior matching production APIs; server-side integration remains covered elsewhere.

## Test Signals
This is direct test code using assertEquals, when to exercise the behavior described above.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/keys/TestChecksumKeyHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/keys/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/keys/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell.keys`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Test integration uses JUnit, Mockito, command-line parsing, and captured streams rather than a live OM unless explicitly configured by the test.

## Risks and Edge Cases
Tests rely on command-line parsing and mock behavior matching production APIs; server-side integration remains covered elsewhere.

## Test Signals
This is direct test code using JUnit assertions to exercise the behavior described above.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/keys/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/package-info.java -->

# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/package-info.java

## Purpose
Doc-only package descriptor for `org.apache.hadoop.ozone.shell`; it anchors package documentation and package-level annotations for the Ozone shell sources. This research is based on a complete read of the 22-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The file is loaded by Java tooling as package documentation; behavior is supplied by sibling classes in the same package.

## State and Persistence
No mutable state or persistence; only package metadata.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Test integration uses JUnit, Mockito, command-line parsing, and captured streams rather than a live OM unless explicitly configured by the test.

## Risks and Edge Cases
Tests rely on command-line parsing and mock behavior matching production APIs; server-side integration remains covered elsewhere.

## Test Signals
This is direct test code using JUnit assertions to exercise the behavior described above.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/test/java/org/apache/hadoop/ozone/shell/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/dev-support/findbugsExcludeFile.xml -->

# sources/object-store/apache-ozone/hadoop-ozone/client/dev-support/findbugsExcludeFile.xml

## Purpose
Build-support SpotBugs/FindBugs exclusion file that suppresses selected static-analysis findings for the Ozone client module. This research is based on a complete read of the 20-line source file.

## Important APIs and Types
No public runtime API; this file contributes package/build metadata.

## Control Flow
No runtime control flow. The XML is consumed by static-analysis tooling during Maven/QA runs to filter known findings.

## State and Persistence
Persists static-analysis policy in source control only; it does not affect runtime server state.

## Dependencies and Integration Points
This file integrates with the Maven/SpotBugs quality gate for the client module.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/pom.xml -->

# sources/object-store/apache-ozone/hadoop-ozone/client/pom.xml

## Purpose
Build-support SpotBugs/FindBugs exclusion file that suppresses selected static-analysis findings for the Ozone client module. This research is based on a complete read of the 149-line source file.

## Important APIs and Types
Artifact/build declarations include `hdds-hadoop-dependency-client`, `ozone-client`, `jackson-annotations`, `jcip-annotations`, `guava`, `jakarta.annotation-api`, `commons-collections4`, `commons-lang3`, `hadoop-common`, `hdds-client`, `hdds-common`, `hdds-config`, `hdds-erasurecode`, `hdds-interface-client`, `ozone-common`, `ozone-interface-client`, `ratis-common`, `ratis-thirdparty-misc`.

## Control Flow
No runtime control flow. The XML is consumed by static-analysis tooling during Maven/QA runs to filter known findings.

## State and Persistence
Persists static-analysis policy in source control only; it does not affect runtime server state.

## Dependencies and Integration Points
This descriptor feeds Maven reactor builds and publishes the `ozone-client` module consumed by CLI and application code.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
No direct test file is paired in this item; validation should include command parser tests and mocked ObjectStore/OzoneBucket interaction tests.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/BucketArgs.java -->

# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/BucketArgs.java

## Purpose
Immutable client-side argument object and builder used when creating or linking Ozone buckets, including ACLs, metadata, quotas, layout, owner, encryption, and default replication. This research is based on a complete read of the 286-line source file.

## Important APIs and Types
Types: `encapsulates`, `BucketArgs`, `that`, `Builder`. Important methods: `getVersioning`, `getStorageType`, `getAcls`, `getMetadata`, `getEncryptionKey`, `getDefaultReplicationConfig`, `newBuilder`, `getSourceVolume`, `getSourceBucket`, `getQuotaInBytes`, `getQuotaInNamespace`, `getBucketLayout`.

## Control Flow
Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Instances are immutable after `Builder.build()`: ACLs and metadata are copied into immutable collections, quota defaults use `OzoneConsts.QUOTA_RESET`, and all persistence happens later through client APIs that consume the object.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.client` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: HDDS config/replication helpers.

## Risks and Edge Cases
Builder accepts nullable fields and performs little validation; callers and server-side code must enforce semantic constraints.

## Test Signals
Builder immutability/defaults are unit-testable through getter assertions and mutation-after-build checks.

<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/BucketArgs.java -->
