# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/Token.java

## Purpose

`Token` is the client-side serialized form of a Hadoop security token, containing identifier bytes, password bytes, kind, and service. It also locates identifier classes and renewers at runtime.

## Important APIs, Types, and Functions

Constructors build tokens from identifiers/secret managers, raw components, defaults, or copies. APIs include getters/setters, `decodeIdentifier`, `privateClone`, Writable `readFields`/`write`, URL-safe base64 encode/decode, `equals`, `hashCode`, `toString`, `buildCacheKey`, `isManaged`, `renew`, and `cancel`. Nested `PrivateToken` hides HA failover clones, and nested `TrivialRenewer` is the fallback renewer.

## Control Flow

`decodeIdentifier` discovers `TokenIdentifier` implementations via `ServiceLoader`, caches kind-to-class mapping, instantiates the matching class, and reads identifier bytes. Writable serialization writes identifier/password lengths followed by kind and service. Renewer lookup uses a static `ServiceLoader<TokenRenewer>`, selects the first renewer handling the token kind, caches it per token, and falls back to `TRIVIAL_RENEWER`.

## State and Persistence Behavior

Token state is mutable byte arrays, kind, service, and cached renewer. Tokens persist through Writable and URL-safe base64 encodings, and are stored in `Credentials` token files. The identifier-class map and renewer loader are static process state.

## Dependencies and Integration Points

It depends on Hadoop `Writable`, `Text`, `ReflectionUtils`, `Configuration`, `TokenIdentifier`, `TokenRenewer`, `SecretManager`, ServiceLoader, Base64, and `Credentials` workflows. It is central to delegation tokens and authentication.

## Risks and Edge Cases

`getIdentifier` and `getPassword` expose mutable arrays. ServiceLoader implementation failures are skipped at debug level, which can leave identifiers undecodable or renewers missing. Equality requires exact runtime class, so `PrivateToken` differs from public tokens. Hash code only uses identifier bytes while equality includes password/kind/service.

## Test Signals

Tests should cover Writable and URL round trips, null constructor components, identifier decoding via ServiceLoader, unknown kind behavior, private clone equality/service behavior, renewer selection/fallback, managed renew/cancel delegation, mutable-array exposure assumptions, and cache key stability.
