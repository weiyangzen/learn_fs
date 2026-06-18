# sources/distributed-fs/openafs/src/rxgen/rpc_errors.h

## Purpose
`rpc_errors.h` defines error constants used by rxgen-generated client/server marshalling and unmarshalling paths.

## Important APIs, Types, and Functions
- `RXGEN_CC_MARSHAL`, `RXGEN_CC_UNMARSHAL`, `RXGEN_SS_MARSHAL`, and `RXGEN_SS_UNMARSHAL` are negative generated-stub error codes.
- `VICETOKENDEAD` is a positive legacy error code noted as needing relocation.

## Control Flow
No runtime control flow.

## State and Persistence
No state; compile-time constants only.

## Dependencies and Integration Points
Included by generated or generator support code that needs stable marshalling error values.

## Risks and Edge Cases
Constants must not collide with other OpenAFS/RX error spaces. The comment indicates `VICETOKENDEAD` is misplaced here, which can confuse ownership of error-code definitions.

## Test Signals
Compile generated stubs that reference these constants and verify callers can distinguish client/server marshal and unmarshal failures.
