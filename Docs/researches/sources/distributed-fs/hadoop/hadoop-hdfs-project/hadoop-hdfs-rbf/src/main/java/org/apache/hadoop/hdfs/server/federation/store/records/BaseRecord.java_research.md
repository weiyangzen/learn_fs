<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/BaseRecord.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/BaseRecord.java

## Purpose
Abstract base for all State Store records, defining timestamps, primary keys, comparison, equality, validation, and expiration/deletion hooks.

## APIs, Types, and Functions
Subclasses must implement date created/modified accessors, `getExpirationMs()`, and `getPrimaryKeys()`. Shared methods include `init()`, `getPrimaryKey()`, `generateMashupKey()`, `like()`, `equals()`, `hashCode()`, `compareTo()`, `checkExpired()`, `shouldBeDeleted()`, `validate()`, and `hasOtherFields()`.

## Control Flow, State, and Persistence
`init()` seeds creation and modification time with `Time.now()`. Primary key maps define persisted row identity. Equality and hashing use primary keys, while default ordering is descending modification time. Expiration checks compare driver/current time to modification time and subclass expiration settings; deletion checks only fire for expired records with configured deletion windows.

## Dependencies and Integration
All membership, mount table, router, disabled nameservice, and version records extend this class. State Store drivers call validation, primary-key generation, expiration, and deletion logic when reading/writing records.

## Risks and Test Signals
`compareTo()` casts a long time delta to int, which can overflow for large differences. `validate()` requires positive timestamps, so embedded non-stored records must override timestamp accessors or avoid base validation. State store driver tests, expiration tests, and primary-key equality tests are critical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/BaseRecord.java -->
