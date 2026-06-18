# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FileBasedIPList.java

## Purpose

`FileBasedIPList` loads IP addresses, hostnames, and CIDR ranges from a local text file and answers membership queries through the `IPList` interface.

## Important APIs, Types, And Functions

The constructor takes a file name and builds a `MachineList` from unique file lines. `reload()` returns a new `FileBasedIPList` for the same file. `isIn(String ipAddress)` delegates to `MachineList.includes()`. `readLines()` opens the file as UTF-8, trims and filters comments/empty lines, and deduplicates with a `HashSet`.

## Control Flow, State, And Persistence

If the file does not exist, construction logs a warning and uses an empty `MachineList`. Otherwise it reads the full file once. Instances are immutable after construction; `reload()` does not mutate the existing list. Persistence is entirely external in the watched file.

## Dependencies And Integration Points

It depends on `MachineList`, `IPList`, Java NIO file APIs, and SLF4J. It is used where administrators provide allow/deny lists for network-facing Hadoop services.

## Risks And Test Signals

Membership reflects only the snapshot at construction time. Bad CIDR syntax propagates from `MachineList`; unknown hosts are logged and skipped there. Tests should cover missing files, comments, whitespace, duplicate entries, wildcard/list behavior through `MachineList`, and reload producing a fresh snapshot.
