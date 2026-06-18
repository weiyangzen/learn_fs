<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationKey.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationKey.java

Source read size: 145 lines, 4076 bytes.

## Purpose
Writable value object for delegation-token master keys. It carries a key id, expiry date, and encoded secret key bytes used to generate or verify token passwords.

## Important APIs, Types, and Functions
Constructors accept either a `SecretKey` or encoded bytes. Accessors include `getKeyId()`, `getExpiryDate()`, `setExpiryDate()`, `getKey()`, and `getEncodedKey()`. `write()` and `readFields()` define the wire/storage form; `equals()` and `hashCode()` compare id, expiry, and key bytes. `MAX_KEY_LEN` bounds deserialized key material at 1 MiB.

## Control Flow, State, and Persistence Behavior
The object is simple mutable state. Serialization writes variable-length key id and expiry, then `-1` for null key bytes or length plus bytes. Deserialization uses `WritableUtils.readVIntInRange()` to reject oversized material before allocating.

## Dependencies and Integration Points
Delegation key maps in `AbstractDelegationTokenSecretManager`, SQL rows, and ZK znodes all serialize this type. It depends on Hadoop `WritableUtils`, Java crypto `SecretKey`, and `AbstractDelegationTokenSecretManager.createSecretKey()` to reconstruct usable secrets.

## Risks and Test Signals
Risks include exposing raw encoded key bytes through `getEncodedKey()`, equality depending on expiry as well as key id, and runtime exceptions for oversized constructor input. Test serialization round trips with null/non-null keys, max-length rejection, secret-key reconstruction, expiry mutation, hash/equals behavior, and compatibility with SQL/ZK persisted bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationKey.java -->
