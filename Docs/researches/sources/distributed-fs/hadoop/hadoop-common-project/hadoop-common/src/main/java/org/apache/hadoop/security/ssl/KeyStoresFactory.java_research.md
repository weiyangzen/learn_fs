# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/KeyStoresFactory.java

## Purpose

`KeyStoresFactory` abstracts SSL key manager and trust manager creation for Hadoop's `SSLFactory`.

## Important APIs, Types, and Functions

It extends `Configurable` and declares `init(SSLFactory.Mode)`, `destroy`, `getKeyManagers`, and `getTrustManagers`.

## Control Flow

Implementations initialize key/trust managers for client or server mode and expose the arrays to `SSLFactory`.

## State and Persistence Behavior

The interface owns no state. Implementations may read keystore files, schedule reloads, or hold manager arrays.

## Dependencies and Integration Points

It depends on JSSE `KeyManager`/`TrustManager`, `SSLFactory.Mode`, and Hadoop configuration. `SSLFactory` creates the configured implementation through reflection.

## Risks and Edge Cases

Custom implementations must match JSSE expectations and clean up resources in `destroy`. Null trust managers may intentionally mean default trust behavior depending on SSL context setup.

## Test Signals

Tests should verify custom factory selection by configuration, mode-specific initialization, returned manager arrays, and cleanup.
