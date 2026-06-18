# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialProvider.java

Purpose: public unstable abstraction for credential/password stores used by Hadoop applications.

Important APIs/types/functions: `CredentialEntry` pairs alias and char[] credential and exposes getters plus a diagnostic `toString`. Provider contract includes `flush`, `getCredentialEntry`, `getAliases`, `createCredentialEntry`, `deleteCredentialEntry`, `isTransient`, `needsPassword`, `noPasswordWarning`, and `noPasswordError`. `CLEAR_TEXT_FALLBACK` exposes the config key controlling clear-text fallback behavior.

Control flow: abstract class only defines contract and defaults. Implementations must be thread-safe. Durable providers override persistence/password methods; transient providers override `isTransient`.

State/persistence: no provider state in base class. `CredentialEntry` stores alias and char[] reference without copying.

Dependencies/integration: `Configuration.getPassword`, `CredentialProviderFactory`, Hadoop credential shell, key store providers, user provider, and common config keys.

Risks: `CredentialEntry.toString` includes credential contents and should not be used in logs; char[] is not defensively copied, so callers and providers can mutate shared material; implementations must enforce thread safety themselves. Test signals include provider contract conformance, transient filtering, password-required messaging, duplicate alias semantics, and avoidance of credential stringification in sensitive logs.
