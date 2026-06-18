# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/UserProvider.java

Purpose: transient credential provider backed by the current user's in-memory Hadoop `Credentials`.

Important APIs/types/functions: `SCHEME_NAME=user`; constructor captures `UserGroupInformation.getCurrentUser()` and a copy of its credentials via `getCredentials`. `isTransient` returns true. Credential operations map aliases to `Text` secret keys. `flush` adds the provider's credentials back to the user. Nested factory creates provider for `user:///`.

Control flow: reads get secret bytes and decode UTF-8 to char[]. Creates reject duplicate aliases, store UTF-8 bytes, and return entry. Deletes require existing secret key. Listing returns all secret-key aliases.

State/persistence: in-memory UGI and `Credentials`. Transient provider does not write durable storage; flush mutates the user's in-memory credentials.

Dependencies/integration: `UserGroupInformation`, `Credentials`, `Text`, credential provider factory, and jobs that distribute credentials through UGI rather than external keystore files.

Risks: constructor uses `getCredentials`, which filters private tokens but copies secret keys; provider may not reflect later UGI credential mutations until flush/add. Secrets pass through immutable `String` for encoding/decoding. Because it is transient, CLI normally avoids selecting it unless explicitly supplied. Test signals include transient filtering, duplicate/missing alias, flush updating current UGI, alias listing, and UTF-8 credential round trip.
