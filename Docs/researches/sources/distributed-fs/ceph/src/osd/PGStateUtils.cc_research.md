# sources/distributed-fs/ceph/src/osd/PGStateUtils.cc

## Purpose
`PGStateUtils.cc` implements lightweight PG state-history instrumentation. It records entry/exit timestamps for nested named states, groups completed state traces by OSD map epoch, stores a bounded recent history, and dumps that history through Ceph's formatter.

## Important APIs and Functions
- `NamedState::NamedState()` captures the current time and calls `PGStateHistory::enter()` when a history object is present.
- `NamedState::~NamedState()` calls `PGStateHistory::exit()` for RAII-style state timing.
- `PGStateHistory::enter()` lazily creates the current `PGStateInstance` and pushes an embedded state.
- `PGStateHistory::exit()` stamps the instance with the current OSD map epoch, records an exit time, and moves a complete instance into the circular buffer when all nested states have exited.
- `PGStateHistory::dump()` emits an array of epochs, each with a sequence of state records containing state name, enter time, and exit time.

## Control Flow
State tracking is stack based. Entering a `NamedState` pushes `(time, state_name)` onto the active instance. Exiting sets the epoch, pops the top embedded state into `state_history`, and if the stack is empty calls `reset()` to move the finished instance into the bounded buffer and clear the active pointer. Dumping iterates only completed instances in the buffer.

## State and Persistence Behavior
State history is in-memory diagnostic state only. `PGStateHistory` keeps at most ten completed `PGStateInstance` objects in a boost circular buffer. It does not serialize to disk. It relies on `EpochSource::get_osdmap_epoch()` at exit time, so the epoch attached to an instance reflects the latest exit, not necessarily every nested state's entry epoch.

## Dependencies and Integration Points
- Includes `PGStateUtils.h` and `common/Clock.h`.
- Uses `ceph_clock_now()` for timestamps and `ceph::Formatter` for dumps.
- Integrated by peering state classes through `NamedState` RAII objects and `PGStateHistory` owned by `PeeringState`.

## Risks and Edge Cases
- `PGStateHistory::exit()` assumes `pi` is non-null and the embedded stack is non-empty; unbalanced enter/exit calls will crash or assert elsewhere.
- `NamedState` stores `state_name` as `const char*`, so callers must pass storage with static or sufficiently long lifetime.
- `dump()` omits the currently active incomplete instance because it only iterates the completed circular buffer.
- Nested state names are recorded by stack order on exit, so history order is exit order, not necessarily entry order.

## Test Signals
Useful tests should create nested `NamedState` scopes, verify a completed history appears only after the outermost exit, check circular-buffer truncation after more than ten instances, and validate formatter field names (`history`, `epochs`, `epoch`, `states`, `state`, `enter`, `exit`). Integration coverage should inspect peering diagnostics after state transitions.
