# sources/distributed-fs/lizardfs/src/protocol/CMakeLists.txt

## Purpose
Builds the LizardFS protocol library and its unit tests.

## Important APIs, Types, And Functions
Includes the protocol source directory, collects `PROTOCOL` sources, builds `lzfsprotocol`, creates the `lzfsprotocol` unittest target from `${PROTOCOL_TESTS}`, and links tests with `mfscommon`.

## Control Flow
CMake source collection feeds both the library and test macro, making protocol headers and helpers available to other components.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on project-local CMake macros `collect_sources`, `create_unittest`, and `link_unittest`. The resulting library is a dependency for components that serialize/deserialize LizardFS wire packets.

## Risks And Edge Cases
Protocol code is mostly header/macros; source collection must include tests and generated/inline-heavy headers correctly. Missing `mfscommon` linkage would break serialization helper tests.

## Test Signals
Successful build and execution of protocol unit tests such as `cltocs_unittest.cc` and `cltoma_unittest.cc`.
