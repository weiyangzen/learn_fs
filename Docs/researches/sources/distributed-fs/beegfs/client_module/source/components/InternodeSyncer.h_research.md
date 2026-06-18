# sources/distributed-fs/beegfs/client_module/source/components/InternodeSyncer.h

## Purpose
Declares the internode synchronization component, delayed-operation entry types, and force-update controls.

## Important APIs and types
Delayed entries store `Time ageT`, duplicated `EntryInfo`, copied file handle IDs, and operation-specific fields: close access flags, append-lock cleanup, max target index, optional file event; entry unlock client FD; range unlock owner PID. `InternodeSyncer` embeds `Thread`, app/config, datagram listener, node stores, management init condition, registration flag, forced target-state flag, state-update timing, and three mutex-protected `PointerList` queues. Public APIs include lifecycle, waiting for management init, adding delayed close/entry-unlock/range-unlock work, queue-size getters, and force-target-state update setters.

## State, dependencies, integration
The header ties together networking, target state, file-event, remoting IO, and threading abstractions. Queue comments make the ownership model explicit: the syncer removes entries to keep iterators valid.

## Risks and test signals
`mgmtInitDone` means initialization phase finished, not necessarily that registration succeeded forever. `InternodeSyncer_setForceTargetStatesUpdate` is edge-triggered and consumed by the loop. Tests should validate delayed entry copying/freeing and forced-update reset behavior.
