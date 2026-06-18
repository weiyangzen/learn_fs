# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/FileBasedKeyStoresFactory.java

## Purpose

`FileBasedKeyStoresFactory` loads SSL key managers and trust managers from configured keystore/truststore files and schedules reload checks when those files change.

## Important APIs, Types, and Functions

It implements `KeyStoresFactory` with `setConf`, `getConf`, `init`, `destroy`, `getKeyManagers`, and `getTrustManagers`. It defines client/server property templates for keystore, truststore, passwords, types, and reload intervals, plus `resolvePropertyName` and `getPassword`.

## Control Flow

`init` reads whether client certs are required, creates a daemon `Timer`, resolves mode-specific keystore/truststore type and paths, and either loads a reloading keystore manager or creates an empty keystore-backed manager for clients that do not need certs. If a truststore location is configured, it creates a `ReloadingX509TrustManager`. For positive reload intervals, it schedules `FileMonitoringTimerTask` instances that call manager `loadFrom`.

## State and Persistence Behavior

State includes loaded key manager arrays, trust manager arrays, optional reloading trust manager, and a timer. It reads local keystore/truststore files and credential-provider passwords but writes nothing. `destroy` cancels the timer and clears manager references when a trust manager exists.

## Dependencies and Integration Points

It depends on `SSLFactory.Mode`, `ReloadingX509KeystoreManager`, `ReloadingX509TrustManager`, `FileMonitoringTimerTask`, JSSE `KeyStore`/`KeyManagerFactory`, Hadoop `Configuration.getPassword`, and credential-provider integration.

## Risks and Edge Cases

Server mode and client-cert-required mode require keystore location and password. Empty truststore password is treated as null and allowed. `destroy` only clears manager arrays inside the `trustManager != null` branch, so client/server configurations without truststore keep arrays after timer cancellation. Reload failure logs and keeps existing managers.

## Test Signals

Tests should cover client/server property resolution, missing keystore failures, credential-provider password lookup, empty truststore password, reload interval zero and positive scheduling, truststore absence, timer cancellation, and reload preserving previous state on failure.
