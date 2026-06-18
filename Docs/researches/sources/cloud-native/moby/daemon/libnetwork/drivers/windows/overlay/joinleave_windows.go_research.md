# sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/joinleave_windows.go

Purpose: Implements Windows overlay join and NetworkDB peer event handling using HNS-backed endpoints and the shared overlay peer record schema.

Important APIs and functions: `Join` validates ids, finds network/endpoint, marshals a shared `overlay.PeerRecord` with endpoint IP/MAC and provider address, publishes it via `JoinInfo.AddTableEntry`, and disables gateway service when endpoint state requests it. `EventNotify` filters non-overlay peer table events, ignores local peers, decodes previous/new peer records, and calls Windows `peerDelete`/`peerAdd`. `DecodeTableEntry` returns nil data on Windows. `Leave` only validates ids.

Control flow: event handling mirrors Linux differential peer update logic but delegates to Windows HNS peer functions.

State and persistence: no datastore here. Mutates NetworkDB table entries through join info and HNS peer state through peer add/delete in another file.

Dependencies and integration points: integrates Windows overlay with shared Linux overlay protobuf/API package, libnetwork table watcher, and HNS peer database.

Risks: `Leave` does not remove local peer state directly; cleanup relies on endpoint/network lifecycle and NetworkDB. `DecodeTableEntry` is unimplemented, so diagnostics are weaker than Linux.

Test signals: no direct Windows overlay tests in this subset.
