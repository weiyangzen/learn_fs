# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/Credentials.java


Purpose: `Credentials` is Hadoop's in-memory and serialized container for delegation tokens and secret keys. It is used by MapReduce, YARN, HDFS, and IPC paths to pass authentication material between processes.

Important APIs and types: The class implements `Writable`. `SerializedFormat` supports `WRITABLE` and `PROTOBUF`. Public operations include token and secret CRUD, unmodifiable map views, file/stream read-write helpers, `writeTokenStorageToStream()`, `writeTokenStorageFile()`, `readTokenStorageFile()`, `addAll()`, and `mergeAll()`.

Control flow: Tokens are keyed by `Text` alias in `tokenMap`; secrets are byte arrays keyed by `Text` in `secretKeysMap`. `addToken()` ignores null tokens and, when replacing a token, updates private clones whose base alias matches the replaced alias. Storage files start with magic `HDTS`, then a format byte, then either Writable records or a delimited protobuf. Writable serialization writes token count and token entries first, then secret count and byte payloads. Protobuf serialization converts tokens through shaded protobuf helpers and stores alias bytes plus token/secret fields.

State and persistence: Runtime state is mutable and not synchronized. Persistence is explicit through Hadoop `Path`, Java `File`, `DataInputStream`, or `DataOutputStream`. The default writer keeps the older Writable format for compatibility, while protobuf can be requested.

Dependencies and integration: It depends on Hadoop `Token`, `TokenIdentifier`, `WritableUtils`, `Text`, filesystem APIs, shaded protobuf helpers, and IO cleanup utilities. It is a core integration type for token storage files, job credentials, and UGI token propagation.

Risks and test signals: Tests should cover format magic validation, unknown format handling, Writable/protobuf round trips, private clone replacement, overwrite versus merge behavior, null-token logging, and alias byte preservation. Security risks include mutable byte-array secrets returned directly and accidental persistence of sensitive keys to broadly readable files.
