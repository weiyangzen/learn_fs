# sources/distributed-fs/ceph-client/tools/perf/util/thread-stack.h

## Purpose

`thread-stack.h` defines the public interface for synthesized thread stacks and call/return export.

## Important APIs, Types, and Functions

The call-return flag bits are `CALL_RETURN_NO_CALL`, `CALL_RETURN_NO_RETURN`, and `CALL_RETURN_NON_CALL`. `struct call_return` carries paired call and return metadata: thread, comm, call path, call/return times, branch/instruction/cycle deltas, sample references, database IDs, parent ID, and flags. `struct call_return_processor` owns a `call_path_root`, callback, and opaque data. The header exports stack event, sample, branch sample, flush/free/depth, processor allocation, and `thread_stack__process()`.

## Control Flow and State

Callers feed branch samples into this API. Simple users ask for synthesized callchains later; export users provide a processor callback that receives completed call-return records.

## Dependencies and Integration Points

The API references perf sample, address-location, call-path, symbol, dso, comm, and thread structures without forcing all definitions into the header. It is used by callchain and branch-history consumers.

## Risks and Test Signals

Consumers must keep callback data valid and respect that flush may emit incomplete calls. Compile tests should catch signature drift; behavior tests should verify flag combinations and parent db-id assignment.
