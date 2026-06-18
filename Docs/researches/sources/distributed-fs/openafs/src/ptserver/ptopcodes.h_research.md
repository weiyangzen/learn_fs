# sources/distributed-fs/openafs/src/ptserver/ptopcodes.h

## Purpose
Defines numeric opcode constants for the protection-server RPC interface.

## Important APIs, Types, And Functions
Defines `LOWEST_OPCODE` as 500, opcodes from `PRINEWUSER` through `PRLISTSUPERGROUPS`, and `HIGHEST_OPCODE` as 530. Constants cover create, lookup, dump, membership, ID/name translation, delete, CPS, list/set max, change entry, list elements/entries/owned/supergroups, host CPS, and update entry operations.

## Control Flow
There is no runtime behavior. Generated or hand-written RPC dispatch code uses these numeric constants to identify protection operations.

## State And Persistence
The file defines protocol constants only. These values are persistent wire/API contract state and must remain stable for compatibility.

## Dependencies And Integration Points
Integrated with `ptint.xg`, ptserver RPC stubs, and clients that need explicit operation numbers.

## Risks And Test Signals
Risks are opcode collisions, changing existing values, or failing to update `HIGHEST_OPCODE` when adding operations. Test signals are RPC compatibility between clients and servers and generated interface consistency.
