# sources/distributed-fs/lizardfs/src/uraft/uraftstatus.cc

## Purpose
`uraftstatus.cc` adds a TCP status endpoint to uRaft. It accepts client connections and returns a text snapshot of the local election state, leader identity, promotion block state, and per-node votes/heartbeats/versions when relevant.

## Important APIs, Types, and Functions
`uRaftStatusConnection` owns one TCP socket and response buffer; `init()` writes the prepared buffer asynchronously. `uRaftStatus` implements `init()`, `set_options()`, `storeData()`, and `acceptConnection()`. `storeData()` formats fields from inherited `state_`, `node_`, `opt_`, and `block_leader_promotion_`.

## Control Flow
`uRaftStatus::init()` first initializes the base uRaft election engine, then opens, binds, and listens on the configured status TCP port. `acceptConnection()` allocates a shared connection, accepts asynchronously, fills the response buffer with `storeData()`, starts async write, and immediately re-arms accept for the next client.

## State and Persistence Behavior
The status layer is runtime-only. It exposes inherited volatile election state and does not persist or mutate leadership. Each connection owns its response buffer long enough for async write through `shared_from_this()`.

## Dependencies and Integration Points
The file uses Boost.Asio TCP acceptor/socket/write and Boost.Format. It is inherited by `uRaftController`, and external tools can query the TCP port for operational diagnostics.

## Risks and Edge Cases
The status format is plain text and appears intentionally human-oriented, including the misspelled `"I'M THE BOOSSSS"` marker. Consumers should not assume a stable machine protocol unless maintained. `boost::format("%i")` is used with `uint64_t` fields, which can truncate or format incorrectly on some platforms. Accept errors are ignored and accept is always rearmed.

## Test Signals
Tests should connect to the status port and verify key fields after follower/candidate/leader transitions, blocked promotion, and per-node arrays. Compatibility tests should catch accidental changes if scripts parse the text.
