# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LimitInputStream.java

## Purpose

`LimitInputStream` is Hadoop's copy of Guava's limited input stream, capping the number of bytes that can be read or skipped from an underlying stream.

## Important APIs, Types, And Functions

The constructor accepts an `InputStream` and nonnegative byte limit. It overrides `available()`, `mark()`, `read()`, `read(byte[],int,int)`, `reset()`, and `skip()` while tracking remaining bytes in `left` and marked remaining bytes in `mark`.

## Control Flow, State, And Persistence

Reads return EOF once `left` reaches zero. Bulk reads clamp length to `left` and subtract successful bytes read. `skip()` clamps similarly. `mark()` records the current remaining limit even if the underlying stream does not support reset; `reset()` validates support and mark presence before restoring `left`. State is per-stream wrapper only.

## Dependencies And Integration Points

It depends on `FilterInputStream` and Hadoop `Preconditions`. It is used where callers must expose only a bounded segment of a larger stream.

## Risks And Test Signals

The wrapper does not close early at the limit; it simply returns EOF. Tests should cover zero limit, negative limit rejection, single and bulk reads, skip, available clamping, mark/reset success and failure, and EOF behavior from the underlying stream.
