# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogOpCodes.java

## Purpose

`FSEditLogOpCodes` is the stable byte-code registry for HDFS edit-log records. Each enum constant maps a one-byte value from the edits file to the nested `FSEditLogOp` subclass that knows how to read, write, and render that operation. The enum is part of the on-disk wire format: byte values are historical compatibility commitments, not local implementation details.

## Important APIs, Types, and Functions

Each enum value stores `opCode` and optionally `opClass`. `getOpCode()` returns the durable byte value. `getOpClass()` returns the `FSEditLogOp` nested class used by `FSEditLogOp.OpInstanceCache` to create reusable operation instances.

The enum covers current and legacy operations from `OP_ADD` byte `0` through erasure-coding operations at bytes `49` to `52`, plus `OP_INVALID` at byte `-1`. Deprecated or obsolete entries remain present, including datanode add/remove and namespace quota variants, because old edit logs may still contain them or tooling may need to recognize them.

The static `VALUES` array is built once from the maximum non-negative byte code. `fromByte(byte opCode)` returns the enum for non-negative values inside the array, `OP_INVALID` for `-1`, and `null` for unknown bytes. This is the fast path used by edit-log readers for every record.

## Control Flow

During `FSEditLogOp.Reader.decodeOp()`, a byte is read from the stream and passed to `fromByte`. If the result is `OP_INVALID`, the reader verifies the log terminator. If the result has no op class or is `null`, the reader throws an invalid-opcode error. Otherwise `OpInstanceCache.get(opCode)` uses `getOpClass()` to instantiate or retrieve the matching `FSEditLogOp` subclass and then delegates payload decoding to that class.

During writes, `FSEditLogOp.Writer.writeOp()` asks the operation object for `op.opCode.getOpCode()` and writes that byte as the first byte of the frame. The opcode therefore controls both dispatch and durable compatibility.

## State and Persistence Behavior

The enum itself has no mutable runtime state after static initialization, but it defines the persistent edit-log namespace. `OP_INVALID` is not a normal operation; it is the terminator marker recognized by readers. The comment notes that valid opcodes are currently in the `0..127` range. Negative values other than `-1` are rejected by `fromByte`.

Because `VALUES` is indexed by byte code, sparse missing values would produce `null` entries. Existing code handles `null` by treating it as invalid. Adding a new opcode should append a new unused byte and map it to an operation class; changing existing byte assignments would corrupt compatibility with all previously written edit logs.

## Dependencies and Integration Points

The enum imports all nested `FSEditLogOp` classes and is used by `FSEditLogOp.OpInstanceCache`, edit-log readers/writers, offline edit viewers, inotify translation, and tests that assert opcode counts. It integrates with `FSEditLogLoader` indirectly because loader switch/dispatch behavior depends on the same op identities after decoding.

## Risks

The main risk is compatibility drift. Reassigning byte values, deleting obsolete constants, or changing an op class mapping can make old logs unreadable or make readers instantiate the wrong payload parser. Adding a constant without updating `FSEditLogOp`, replay logic, offline edits viewer expectations, and inotify handling can produce invalid-opcode failures or unsupported operation gaps.

There is also a guardrail risk around `VALUES`: the table is sized by maximum non-negative opcode, so non-contiguous codes are allowed but unknown holes return `null`. Code that assumes every value below `VALUES.length` is non-null would be incorrect.

## Test Signals

`TestDFSInotifyEventInputStream` asserts the total enum length, which is a useful signal when adding an opcode because inotify translator coverage may need adjustment. `TestOfflineEditsViewer` iterates `FSEditLogOpCodes.values()` and maintains a skipped-op set for unsupported/deprecated operations, so opcode additions commonly require viewer-test updates. Edit-log replay and journal tests such as `TestFileJournalManager`, `TestEditsDoubleBuffer`, and restart tests provide indirect validation that byte-to-class mapping still works.
