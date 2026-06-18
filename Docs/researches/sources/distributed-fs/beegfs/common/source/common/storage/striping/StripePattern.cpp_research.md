<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.cpp

Purpose: Implements polymorphic stripe-pattern deserialization, type naming, and common equality checks.

Important APIs/functions: `StripePattern::deserialize` reads `StripePatternHeader`, creates `Raid0Pattern`, `Raid10Pattern`, or `BuddyMirrorPattern`, deserializes content, and marks the deserializer bad on invalid type/chunk size/content. `getPatternTypeStr` formats pattern types. `stripePatternEquals` compares type, chunk size, storage pool ID, then delegates derived content equality.

Control flow/state/persistence: Deserialization is a factory with strict validation and cleanup on failure. It supports old/no-pool-id payloads through header flags.

Dependencies/integration: Includes all derived pattern classes, serialization, logging, and `StringTk`. Used whenever patterns are loaded from metadata or messages.

Risks/test signals: Compatibility with pre-pool-id formats is central. Tests should cover invalid type, zero chunk size, malformed content, no-pool flag, storage pool ID comparison, and all derived type round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.cpp -->
