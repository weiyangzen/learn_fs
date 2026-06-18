# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.security.authorize` as Hadoop's service-level authorization support package.

## Important APIs, Types, and Functions

It declares package annotations `@InterfaceAudience.Public` and `@InterfaceStability.Evolving`.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

The file owns no state or persistence.

## Dependencies and Integration Points

It imports Hadoop classification annotations and applies them to the package containing ACLs, proxy-user authorization, policy providers, and service authorization management.

## Risks and Edge Cases

The main risk is documentation/annotation drift if package audience or stability changes.

## Test Signals

Compile/package-javadoc generation is the relevant signal.
