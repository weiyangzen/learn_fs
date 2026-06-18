# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/ReloadingX509TrustManager.java

## Purpose

`ReloadingX509TrustManager` is an `X509TrustManager` wrapper that atomically reloads truststore contents when requested.

## Important APIs, Types, and Functions

The constructor loads an initial trust manager. It implements `checkClientTrusted`, `checkServerTrusted`, `getAcceptedIssuers`, and `loadFrom(Path)`.

## Control Flow

`loadTrustManager` reads the truststore file, initializes `TrustManagerFactory`, selects the first `X509TrustManager`, and returns it. Trust checks delegate to the current atomic reference or throw `CertificateException` if no manager is available. `loadFrom` wraps failures in `RuntimeException` with a reload message.

## State and Persistence Behavior

State is the truststore type/password and atomic delegate reference. It reads local truststore files and writes nothing.

## Dependencies and Integration Points

It depends on JSSE trust APIs, `SSLFactory.TRUST_MANAGER_SSLCERTIFICATE`, and `FileBasedKeyStoresFactory` file monitoring.

## Risks and Edge Cases

No selected X509 trust manager yields null and causes trust checks to fail. `getAcceptedIssuers` returns an empty static array when no delegate exists. Reload failures must be handled by scheduler callbacks to preserve operational behavior.

## Test Signals

Tests should cover initial truststore load, client/server trust delegation, accepted issuer output, successful reload, invalid reload failure, null-password truststore, and missing X509 manager behavior.
