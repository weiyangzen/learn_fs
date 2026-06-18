# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenSelector.java

## Purpose

`TokenSelector` is the interface for choosing an appropriate token for a named service from a collection of available tokens.

## Important APIs, Types, and Functions

It declares `selectToken(Text service, Collection<Token<? extends TokenIdentifier>> tokens)`.

## Control Flow

Implementations inspect token kind/service fields and return a matching token or null.

## State and Persistence Behavior

The interface owns no state and does not mutate token persistence.

## Dependencies and Integration Points

It depends on `Text`, `Token`, and `TokenIdentifier`. It is referenced by `TokenInfo` and used by clients/RPC code selecting credentials.

## Risks and Edge Cases

Selectors must handle null or empty token collections consistently. Overly broad selectors can return tokens for the wrong service.

## Test Signals

Tests should cover matching service, non-matching service, multiple-token ordering, null/empty collections, and integration with `TokenInfo`.
