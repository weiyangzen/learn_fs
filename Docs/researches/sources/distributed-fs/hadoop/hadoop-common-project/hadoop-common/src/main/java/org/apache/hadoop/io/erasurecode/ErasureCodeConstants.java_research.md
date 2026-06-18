# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodeConstants.java

Purpose: shared constant names for built-in erasure codecs and raw coder implementations.

Important APIs and control flow: defines codec names such as `rs`, `rs-legacy`, `xor`, and `hhxor`, plus coder names such as `rs_java`, `rs_native`, `xor_java`, `xor_native`, and `dummy`. No executable methods.

State and persistence: static constants only.

Dependencies and integration: referenced by `CodecUtil`, codec/coder classes, and raw coder factories to avoid string drift in configuration and registration.

Risks and test signals: tests should catch renamed constants through codec factory/configuration integration. Changing values is a compatibility risk for persisted EC policies and configuration keys.
