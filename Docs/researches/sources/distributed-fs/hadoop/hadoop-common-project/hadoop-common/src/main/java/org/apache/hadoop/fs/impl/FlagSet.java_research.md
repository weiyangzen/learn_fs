# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FlagSet.java

## Purpose
Generic enum flag container that can be built from configuration and probed as StreamCapabilities.

## Important APIs, Types, and Functions
createFlagSet overloads, buildFlagSet(), enable/disable/set(), enabled(), flags(), hasCapability(), makeImmutable(), pathCapabilities(), copy(), toConfigurationString(), equals/hashCode.

## Control Flow
Constructor copies initial flags and maps prefixed enum names to values. Mutations check the immutable AtomicBoolean. hasCapability resolves capability strings through the prefixed map. buildFlagSet delegates parsing to Configuration.getEnumSet.

## State and Persistence Behavior
Mutable until makeImmutable; after that mutation methods throw. No persistence except configuration string serialization.

## Dependencies and Integration Points
Depends on ConfigurationHelper, Configuration, StreamCapabilities, EnumSet. Useful for filesystem feature flags and path capability exposure.

## Risks and Test Signals
Risks include no synchronization while mutable, hashCode considering only flags while equals includes enumClass/prefix, capability case conventions, and immutable copy behavior. Tests should cover parsing, unknown values, capability names, immutability, equals/hashCode contract, and concurrent read after immutable.
