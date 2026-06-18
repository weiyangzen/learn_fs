# sources/distributed-fs/openafs/src/WINNT/afsd/smb3.h

## Purpose
Defines the Windows afsd SMB dialect-3/NT transaction contract: transaction packet state, dispatch table entries, packed on-wire response structures, and prototypes for Transaction, Transaction2, RAP, NT transact, AndX operations, notify, and extended-security helpers.

## Important APIs, Types, And Functions
`smb_tran2Packet_t` accumulates multi-part transaction parameter/data bytes, identity (`vcp`, `tid`, `uid`, `pid`, `mid`), opcode, named-pipe metadata, decoded strings, and response/error state. `smb_tran2Dispatch_t` maps sub-opcodes to handlers. Packed structures include `smb_tran2QFSInfo_t`, `smb_tran2QPathInfo_t`, `smb_tran2QFileInfo_t`, `smb_tran2Find_t`, and SMB3 file attribute records. Externs cover session setup, tree connect, transaction parsing, RAP share/workstation/server info, file and directory search, info get/set, FSCTL/IOCTL, DFS, NT create/transact/cancel/rename, notify, SID extraction, and `smb3_Init`.

## Control Flow
Implementations build or extend `smb_tran2Packet_t`, dispatch through `smb_tran2DispatchTable` or `smb_rapDispatchTable`, allocate response packets with `smb_GetTran2ResponsePacket`, send them with `smb_SendTran2Packet`, then release state with `smb_FreeTran2Packet`. Packed unions are copied directly into SMB buffers.

## State And Persistence
The header defines transient per-request state only. Durable effects happen in handlers that open files, mutate attributes, enumerate directories, or register notifications.

## Dependencies And Integration Points
Depends on SMB connection/packet types, cache scache types, Windows `FILETIME`/`LARGE_INTEGER`/SID APIs, and client string abstractions. Integrates with `smb3.c`, `smb.c`, named-pipe RPC, DFS, directory enumeration, and cache-manager metadata conversion.

## Risks
Wire layout depends on packing and byte counts. Name arrays and transaction length counters require strict bounds checks. Opcode table sizes must stay synchronized with handler registration.

## Test Signals
Exercise SMB1/NT clients querying file/path/FS info, long Unicode names, find pagination, named-pipe transactions, NTCreateX/locking, DFS referrals, and notify delivery after file changes.
