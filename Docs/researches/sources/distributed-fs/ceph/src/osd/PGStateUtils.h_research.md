# sources/distributed-fs/ceph/src/osd/PGStateUtils.h

## Purpose
`PGStateUtils.h` declares the diagnostic state-history helpers used around PG peering state transitions. The file provides an abstract epoch source, an RAII state marker, a per-epoch state instance, and a bounded history container.

## Important APIs and Types
- `EpochSource` is a small interface exposing `get_osdmap_epoch()`.
- `NamedState` holds a `PGStateHistory*`, `state_name`, and `enter_time`; its constructor/destructor enter and exit the named state.
- `state_history_entry` is `(enter_time, exit_time, state_name)`.
- `embedded_state` is `(enter_time, state_name)` for active nested states.
- `PGStateInstance` stores one epoch's `state_history` and stack of active `embedded_states`; `enter_state()` pushes and `exit_state()` pops into history.
- `PGStateHistory` owns the current instance, a circular buffer of ten completed instances, an `EpochSource`, and dump/current-state helpers.

## Control Flow
Clients typically allocate `NamedState` at the start of a state scope. That constructor delegates to `PGStateHistory::enter()`. Scope exit triggers the destructor, which delegates to `PGStateHistory::exit()`. `PGStateInstance` manages nesting with a stack; `PGStateHistory::reset()` moves completed instances into the circular buffer and clears active state.

## State and Persistence Behavior
All state is transient and diagnostic. The bounded buffer avoids unbounded memory growth in long-running OSDs. `get_current_state()` returns `"unknown"` when there is no active instance and otherwise returns the top embedded state's name. No object-store or monitor persistence is involved.

## Dependencies and Integration Points
- Depends on `epoch_t`, `utime_t`, and `ceph::Formatter`.
- Uses `boost::circular_buffer` and `std::stack` to bound completed history while representing nested active states.
- `PeeringState` owns/uses these helpers for state-machine diagnostics.

## Risks and Edge Cases
- `PGStateInstance::exit_state()` does not validate that the requested state name matches the stack top; misuse can record misleading histories.
- `get_current_state()` assumes that a non-null active instance has at least one embedded state.
- `const char*` state names are not copied into `std::string`; dynamic strings with shorter lifetime are unsafe.
- The circular buffer size is fixed at ten; longer debugging windows require code changes or external logging.

## Test Signals
Tests should cover balanced and nested enter/exit, `get_current_state()` before/during/after active states, history buffer rollover, and formatter output shape. Misbalanced enter/exit behavior is a risk worth catching with debug or death tests if the surrounding framework supports them.
