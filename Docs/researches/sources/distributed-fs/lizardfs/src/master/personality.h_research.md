# sources/distributed-fs/lizardfs/src/master/personality.h

## Purpose

`personality.h` declares metadata server personality APIs and the `Personality` enum used to distinguish master and shadow behavior. The source was read as a complete 72-line header.

## Important APIs, Types, and Functions

It declares `enum class Personality { kMaster, kShadow }`, `getPersonality`, `setPersonality`, `personality_validate`, `personality_init`, `isMaster`, `registerFunctionCalledOnPromotion`, and `promoteAutoToMaster`.

## Control Flow

No executable flow is present. The header documents that promotion from shadow to master is allowed but master-to-shadow is forbidden at the intended API level.

## State and Persistence Behavior

The header owns no state. It exposes process-global personality state maintained by the implementation.

## Dependencies and Integration Points

It depends only on `common/platform.h` and is included by master services that conditionally accept connections or register promotion hooks.

## Risks and Edge Cases

Because `setPersonality` is public, misuse can bypass policy unless callers follow the documented contract. Services relying on `isMaster` must handle runtime promotion.

## Test Signals

Compile coverage and service integration tests that confirm shadow instances reject master-only client connections until promotion.
