# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IPList.java

## Purpose

`IPList` is a tiny membership interface for IP-address allow or deny lists.

## Important APIs, Types, And Functions

The only method is `boolean isIn(String ipAddress)`. `FileBasedIPList` implements it by delegating to `MachineList`.

## Control Flow, State, And Persistence

The interface has no state or persistence. Implementations define parsing, lookup, reload, and thread-safety behavior.

## Dependencies And Integration Points

There are no imports. It integrates with security and networking components that need an interchangeable IP-list source.

## Risks And Test Signals

Callers should not infer whether input is a literal IP, hostname, or CIDR; that is implementation-specific. Tests belong mainly to implementations and should validate null, unknown, wildcard, and CIDR membership behavior.
