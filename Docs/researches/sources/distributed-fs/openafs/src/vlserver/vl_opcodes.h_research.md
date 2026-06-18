# sources/distributed-fs/openafs/src/vlserver/vl_opcodes.h

## Purpose

`vl_opcodes.h` defines the numeric RX operation codes for the VLDB service, currently spanning `501` through `534`. It is a protocol compatibility header consumed by generated stubs, clients, servers, diagnostics, and statistics code.

## Important APIs, Types, And Constants

The constants cover original VL operations (`VLCREATEENTRY` through `VLCHANGEADDR`), N variants for newer entry structures, U variants for UUID/multihome address support, address registration and lookup (`VLREGADDR`, `VLGETADDRSU`), and `VLLISTATTRIBUTESN2`.

## Control Flow

There is no executable flow. Runtime dispatch and generated RX code use these numbers to identify VL RPCs on the wire; `vlclient.c` keeps a parallel ordered name table for statistics display.

## State And Persistence Behavior

The file does not persist state directly, but opcode stability is part of the wire protocol ABI. Reusing or renumbering values would break clients and servers across versions.

## Dependencies And Integration Points

The header is installed under `afs/vl_opcodes.h` by `Makefile.in` and aligns with `vldbint.xg`, VL server implementations, and client calls such as `ubik_VL_RegisterAddrs`.

## Risks And Edge Cases

- Adding a new opcode requires coordinated updates to RXGEN definitions, server implementation, client statistics name tables, and tests.
- `vlclient.c` assumes `VL_NUMBER_OPCODESX` matches the number of entries through `VLLISTATTRIBUTESN2`.

## Test Signals

Protocol tests should verify generated stubs use these numeric values, mixed-version clients can still call old operations, and stats rendering remains aligned when opcodes are added.
