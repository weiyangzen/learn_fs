# sources/distributed-fs/seaweedfs/weed/filer/topics.go

## Purpose

`topics.go` defines filer paths used for SeaweedFS topic metadata and system logs. It was read as a complete 7-line file.

## Important APIs, Types, and Functions

Constants are `TopicsDir = "/topics"`, `SystemLogDir = TopicsDir + "/.system/log"`, and `TopicConfFile = "topic.conf"`.

## Control Flow

No runtime control flow.

## State and Persistence Behavior

The constants identify filer namespace locations where other components store topic configuration and logs.

## Dependencies and Integration Points

Used by topic/log features outside this subset as stable path contracts.

## Risks and Edge Cases

Changing these constants would be a metadata compatibility break for existing topic data.

## Test Signals

Compile-time references and integration tests in topic components should protect these path constants.
