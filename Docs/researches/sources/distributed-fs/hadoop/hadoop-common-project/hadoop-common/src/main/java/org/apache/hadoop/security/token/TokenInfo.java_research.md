# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/TokenInfo.java

## Purpose

`TokenInfo` is a runtime annotation that attaches a token selector type to a protocol or service type.

## Important APIs, Types, and Functions

The annotation has runtime retention, type target, and a single `value()` returning a `Class<? extends TokenSelector<? extends TokenIdentifier>>`.

## Control Flow

There is no executable flow; consumers inspect the annotation reflectively.

## State and Persistence Behavior

The annotation contributes class metadata only.

## Dependencies and Integration Points

It depends on Java annotation APIs and Hadoop token selector/identifier types. Hadoop security/RPC code can use it to choose tokens for a service.

## Risks and Edge Cases

Incorrect selector class metadata causes clients to select the wrong token or none at all. Runtime retention means classpath/reflection availability matters.

## Test Signals

Tests should verify annotated protocol classes expose the intended selector and that token selection code honors the annotation.
