# sources/distributed-fs/eos/mgm/config/QuarkConfigHandler.hh

## Purpose
Declares the MGM QuarkDB configuration storage facade. The header defines the public contract for checking QuarkDB connectivity, reading and writing named configurations, listing live and backup configs, maintaining the changelog, trimming backups, and forming canonical QuarkDB keys.

## Important APIs and Types
- `class QuarkConfigHandler : public eos::common::LogId` provides the API boundary.
- Constructor accepts `QdbContactDetails`, making the handler independent of global connection configuration.
- `common::Status` is the error carrier for synchronous operations.
- `folly::Future<common::Status>` is returned by `writeConfiguration` and `appendChangelog`, explicitly making those persistence operations asynchronous.
- Static key helpers expose the exact hash-key scheme to callers/tests.

## Control Flow and State
The header exposes no inline control flow except key helper declarations and basic method signatures. Private state is `mContactDetails`, `mQcl`, and `mExecutor`, meaning each handler owns its QClient connection and async continuation executor.

## Dependencies and Integration Points
Includes EOS namespace setup, status/logging, QuarkDB contact details, changelog protobuf, standard maps, and Folly futures. It forward declares `folly::Executor` and `qclient::QClient`, minimizing header coupling. Callers include `QuarkDBConfigEngine` and `eos-config-inspect`.

## Risks
- The API exposes asynchronous writes but has no destructor-level draining or cancellation contract in the header.
- Key helpers accept arbitrary names and do not validate characters or prefix collisions.
- `trimBackups` semantics are documented as repeated deletion batches but not as sorted or newest-preserving in the type contract.

## Test Signals
Header-level tests should focus on compile-time integration with callers, async future handling expectations, and static key helper outputs for live, backup, and timestamped backup keys.
