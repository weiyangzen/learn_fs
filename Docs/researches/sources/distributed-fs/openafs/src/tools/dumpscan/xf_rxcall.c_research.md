# sources/distributed-fs/openafs/src/tools/dumpscan/xf_rxcall.c

## Purpose
Implements `XFILE` access over Rx bulk data calls and volume-server dump RPCs. It lets dumpscan read a remote AFS volume dump as an `XFILE`, and it can also wrap an already-created `rx_call`.

## Important APIs, Types, And Functions
Public entry points are `xfopen_rxcall`, `xfopen_voldump`, and `xfon_voldump`. Internal state is `struct rxinfo`, containing an Rx connection, active call, volserver transaction id, and stored result code. Backend callbacks are `xf_rxcall_do_read`, `xf_rxcall_do_write`, `xf_rxcall_do_close`, and `xf_voldump_do_close`.

## Control Flow
`xfopen_rxcall` rejects write-only mode, initializes an `XFILE` backed by `rx_Read`, `rx_Write`, and `rx_EndCall`, and marks writability for `O_RDWR`. `xfopen_voldump` creates a volserver transaction with `AFSVolTransCreate`, starts `StartAFSVolDump`, wraps the resulting call as read-only, and changes close behavior so the volume transaction is ended after the Rx call. `xfon_voldump` parses `volid[@server/partition][,date]`, initializes Rx, resolves server addresses, opens client config, obtains tokens if available, creates rxkad or rxnull security, and starts the remote dump.

## State And Persistence
Per-open state is the active Rx call plus, for volume dumps, the volserver transaction that must be ended on close. There is no local disk persistence. Authentication state is read from the client config and token cache; remote server state includes a busy volume transaction for the duration of the dump stream.

## Dependencies And Integration Points
This file integrates dumpscan with Rx, rxkad/rxnull security, AFS auth and cell config, VL/volser protocol headers, partition parsing, and volserver dump RPCs. `xfiles.c` registers it under the `AFSDUMP` type.

## Risks And Test Signals
The volume-name and volume-id lookup paths are incomplete and currently call `exit(-1)` when server/partition is omitted or a name lookup is needed. On short Rx read, the read callback returns `ERROR_XFILE_RDONLY`, which is semantically surprising for EOF. Security and connection objects are not explicitly destroyed in the shown path. Tests should cover wrapping an existing Rx call, short read/write behavior, transaction cleanup after start failures, explicit server/partition/date parsing, token-present and token-absent security selection, and close result precedence between Rx and `AFSVolEndTrans`.
