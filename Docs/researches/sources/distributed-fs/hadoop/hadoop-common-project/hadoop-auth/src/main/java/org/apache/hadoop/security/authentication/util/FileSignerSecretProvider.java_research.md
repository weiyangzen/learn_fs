<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/FileSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/FileSignerSecretProvider.java

## Purpose
Provides a fixed signing secret loaded from a UTF-8 text file for Hadoop Auth cookie signing.

## Important APIs, types, and functions
`init()` reads `AuthenticationFilter.SIGNATURE_SECRET_FILE`, streams the whole file as characters, converts it to UTF-8 bytes, rejects an empty secret, and exposes it as a one-element `byte[][]`. `getCurrentSecret()` returns the secret; `getAllSecrets()` returns the array used for verification.

## Control flow
If the secret-file property exists, the provider reads the file and initializes `secret`. I/O failures and empty files become runtime exceptions. Finally it sets `secrets = new byte[][] { secret }`.

## State and persistence
The configured secret file is persistent input. The provider keeps the byte secret and array in memory and never reloads the file after init.

## Dependencies and integration points
Used by `AuthenticationFilter` as a `SignerSecretProvider`. Depends on Java NIO file APIs, UTF-8, servlet context arguments, and filter config constants.

## Risks and test signals
If `init()` is called without a file property, `getCurrentSecret()` can return null even though the base contract says it should not. File contents include every character, including trailing newline. Tests should cover missing file property, nonexistent path, empty file fallback behavior in `AuthenticationFilter`, newline preservation, non-ASCII file content, and no-reload semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/FileSignerSecretProvider.java -->
