# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/SecretManager.java

## Purpose

`SecretManager` is the server-side base class for issuing and validating Hadoop token passwords from token identifiers and secret keys.

## Important APIs, Types, and Functions

Subclasses implement `createPassword(T)`, `retrievePassword(T)`, and `createIdentifier`. Optional overrides include `retriableRetrievePassword` and `checkAvailableForRead`. Static crypto APIs include `update(Configuration)`, `createPassword(byte[], SecretKey)`, and `createSecretKey`. It defines nested `InvalidToken`.

## Control Flow

Static initialization calls `update` with default configuration. `update` selects the configured HMAC/key-generator algorithm and key length and warns if key generators, MACs, or secret keys were already initialized. `generateSecret` lazily creates a synchronized `KeyGenerator`. `createPassword` uses a thread-local `Mac` initialized with the supplied secret key to compute the token password.

## State and Persistence Behavior

Static state stores selected algorithm/length and initialization flags; each instance stores a volatile key generator guarded by a lock. No persistence is performed by the base class, but subclasses usually persist secret keys and token records.

## Dependencies and Integration Points

It depends on JCA/JCE `KeyGenerator`, `Mac`, `SecretKey`, Hadoop security configuration keys, `StandbyException`, and `RetriableException`. It underpins delegation-token secret manager implementations.

## Risks and Edge Cases

Changing configuration after crypto objects are initialized logs warnings because existing thread-local MACs/key generators keep older settings. Unsupported algorithms throw `IllegalArgumentException`. `validateSecretKeyLength` assumes byte length times eight equals configured bits.

## Test Signals

Tests should cover algorithm/key-length configuration, update-before/after initialization warnings, password determinism with known keys, unsupported algorithm failures, key length validation, retriable retrieve default behavior, and subclass invalid-token handling.
