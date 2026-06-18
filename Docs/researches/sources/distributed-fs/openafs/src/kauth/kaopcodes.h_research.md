# sources/distributed-fs/openafs/src/kauth/kaopcodes.h

## Purpose
Preserves obsolete numeric KA opcode definitions and optional opcode names for legacy code or debugging references.

## Important APIs, Types, And Functions
Defines opcodes 501 through 510 for SetPassword, Authenticate, GetTicket, SetFields, CreateUser, DeleteUser, GetEntry, ListEntry, ChangePassword, and GetStats, plus `LOWEST_OPCODE`, `HIGHEST_OPCODE`, and `NUMBER_OPCODES`. When `OPCODE_NAMES` is defined, it declares a static `opcode_names` array.

## Control Flow
The header has no runtime control flow. Its comments note that opcodes are now defined by `kauth.rg`.

## State And Persistence
There is no state or persistence.

## Dependencies And Integration Points
It can be included by older tooling that still wants the historic opcode map. The active Rx/RPC dispatch path is generated from `kauth.rg`.

## Risks And Test Signals
The main risk is stale duplication if generated RPC numbers change. Build and debug-output checks are enough; runtime RPC tests should rely on generated interfaces rather than this file.
