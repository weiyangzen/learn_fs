# sources/distributed-fs/openafs/src/volser/dumpstuff.h

## Purpose
Declares the dump/restore entry points and the `iod` compatibility structure used by the volserver dump implementation.

## Important APIs And Types
`struct iod` carries either one RX call or an array of RX calls, dump device/parent/partition context, per-call return codes, and one-character pushback state. Declared functions are `DumpVolume`, `DumpVolMulti`, `RestoreVolume`, and `SizeDumpVolume`.

## Control Flow And State
The header documents the old `qi_in`/stdio-like pushback model. `haveOldChar` and `oldChar` permit a parser to read one byte too far and push it back, but the comments warn that direct `rx_Read` must not bypass this state when a pushed-back byte exists.

## Persistence And Integration
This header does not persist data itself. It ties RX streaming calls to volume objects, restore cookies, and size RPC structures, and is included by dump/restore server code.

## Risks And Test Signals
The main risk is parser inconsistency when code uses raw RX reads while `oldChar` is pending. Multi-dump callers also depend on `codes` alignment with `calls`. Test signals include parser boundary tests around section transitions, multidump partial-failure behavior, and compile/link checks wherever dumpstuff APIs are used.
