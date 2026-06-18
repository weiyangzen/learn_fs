# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/EagerKeyGeneratorKeyProviderCryptoExtension.java

## Purpose
`EagerKeyGeneratorKeyProviderCryptoExtension` is a private KMS server-side decorator for `KeyProviderCryptoExtension`. It pre-generates encrypted data encryption keys and serves them from a `ValueQueue` cache to reduce latency for `generateEncryptedKey`.

## Important APIs, Types, And Functions
The class extends `KeyProviderCryptoExtension` and exposes cache configuration constants under `hadoop.security.kms.encrypted.key.cache.*`: `size` default 100, `low.watermark` default 0.30, `expiry` default 43,200,000 ms, and `num.fill.threads` default 2.

The nested `CryptoExtension` implements `KeyProviderCryptoExtension.CryptoExtension`. It owns the underlying `KeyProviderCryptoExtension` delegate and a `ValueQueue<EncryptedKeyVersion>`.

`EncryptedQueueRefiller.fillQueueForKey(...)` generates the requested number of encrypted keys by repeatedly calling the delegate's `generateEncryptedKey(keyName)` and adds them to the queue. `warmUpEncryptedKeys(...)` initializes queues, `drain(String)` clears a key queue, `generateEncryptedKey(String)` returns `encKeyVersionQueue.getNext(...)`, and decrypt/reencrypt methods delegate directly.

The outer constructor wraps the supplied provider with the eager `CryptoExtension`. Overrides of `rollNewVersion(String)`, `rollNewVersion(String, byte[])`, and `invalidateCache(String)` call the superclass then drain the affected key cache.

## Control Flow
On construction, the cache reads size, low-watermark, expiry, fill-thread count, and `SyncGenerationPolicy.LOW_WATERMARK` from configuration. A request for an encrypted key first asks `ValueQueue` for the next cached value. If the queue needs refill, the refiller generates new encrypted keys through the underlying provider. `ExecutionException` from the queue is translated to `IOException`; `GeneralSecurityException` during refill is also wrapped as `IOException`.

Key version rollover and cache invalidation first perform the delegate operation via `super`, then drain cached encrypted keys for the named key. The comment explicitly notes that asynchronous refill can still race and produce old-version encrypted keys after a drain, but this is accepted because old key versions can still decrypt.

## State And Persistence
Persistent key material remains in the underlying key provider. This class adds transient in-memory per-key queues of encrypted key versions, background refill threads managed by `ValueQueue`, and cache expiry/low-watermark behavior. Drains clear cached values but do not affect stored keys.

## Dependencies And Integration Points
It depends on Hadoop `Configuration`, `KeyProviderCryptoExtension`, `ValueQueue`, and KMS server integration that wraps configured key providers. It is part of KMS encrypted-key generation performance behavior and interacts with key rollover, cache invalidation, decrypt, and reencrypt paths.

## Risks
The cache can serve old-version encrypted keys after rollover because async refill can race with drain. This is intentional but important for clients that might assume rollover immediately changes generated key versions. Cache size/fill threads affect memory, key-provider load, and latency. Wrapping security exceptions as IO exceptions can obscure root cause unless callers inspect causes. Background refill behavior must be thread-safe and bounded.

## Test Signals
Tests should cover cache warmup, low-watermark refill, default and configured cache parameters, propagation/wrapping of generation failures, direct delegation of decrypt/reencrypt, and drain after `rollNewVersion` or `invalidateCache`. Rollover tests should allow old-version encrypted keys while verifying decryptability.
