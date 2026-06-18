# sources/distributed-fs/lizardfs/src/metarestore/merger.h

## Purpose
`merger.h` declares the public metarestore merger interface used by the `metarestore` CLI.

## Important APIs, Types, And Functions
- `int merger_start(const std::vector<std::string>& filenames, uint64_t maxhole)` initializes changelog inputs and id-gap tolerance.
- `uint8_t merger_loop(void)` replays all initialized changelog records and returns a LizardFS status code.

## Control Flow
The header enforces a two-step usage model: initialize with a file list, then call `merger_loop`. It exposes no object handle, indicating that implementation state is process-global.

## State And Persistence
The header itself has no state. Its API implies hidden global state owned by `merger.cc`; callers must not expect multiple independent merger instances.

## Dependencies And Integration Points
It includes `common/platform.h`, `<cstdint>`, `<string>`, and `<vector>`, and is included by `metarestore/main.cc`.

## Risks
- The API lacks an explicit cleanup function and exposes no ownership token, so lifecycle correctness is entirely inside `merger_loop`.
- Return type `uint8_t` conveys LizardFS status values but does not document the status domain in the declaration.

## Test Signals
Compile-time tests are minimal. Behavioral tests should include `merger.h` through `main.cc` or a small harness and verify that one initialized run completes and releases resources.
