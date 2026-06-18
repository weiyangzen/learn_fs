# sources/distributed-fs/openafs/src/vol/fssync-debug.c

Purpose: command-line administration/debug utility for issuing FSSYNC requests and decoding returned volume, vnode, volume-operation, volume-group-cache, and statistics structures. It defines `MAIN` so common OpenAFS globals are provided in this translation unit.

Important APIs/types/functions: `main` registers subcommands with `cmd_CreateSyntax`: `online`, `offline`, `mode/needvolume`, `detach`, `callback/cbk`, `move`, `list/ls`, `leaveoff`, `attach`, `error`, `query/qry`, `header/hdr`, `volop/vop`, `vnode`, `stats`, `vgcquery/vgcqry`, `vgcadd`, `vgcdel`, `vgcscan`, and `vgcscanall`. `common_prolog` initializes server paths, the volume package in `debugUtility` mode, directory package state, reason/program type overrides, and the FSSYNC client connection. `common_volop_prolog`, `vn_prolog`, `do_volop`, and `do_vnqry` build request state. `debug_response` and `read_result` report protocol metadata and handle size mismatches. Demand-attach builds add state/flag stringify helpers for `Volume`, `Vnode`, VLRU, and vnode flags.

Control flow: each command parses common parameters, calls `VConnectFS`, sends an FSSYNC request through client wrappers, prints response metadata, optionally decodes the payload, and disconnects. Non-DAFS builds run `dafs_prolog`, which sends a no-op `LISTVOLUMES` request to detect `SYNC_FLAG_DAFS_EXTENSIONS` and tries to exec a `dafssync_debug` variant if needed. Query commands allocate a maximum protocol response buffer and copy the returned payload into local structures before printing fields.

State and persistence: process-local command state includes selected reason, program type, volume/vnode ids, and partition strings. The tool does not persist files directly, but it can cause fileserver state transitions: taking volumes offline/online, forcing error state, marking moved/done, breaking callbacks, and triggering volume group cache scans.

Dependencies: OpenAFS `cmd` parser, directory/path initialization, volume package initialization, FSSYNC client APIs, protocol string helpers, vnode/volume structs, VGC structs, and Windows event/winsock setup where applicable.

Integration points: operational companion to `fssync-server.c`. It is also a protocol compatibility probe: output warns when DAFS/non-DAFS utility and server extensions do not match. The decoded structures mirror server-side payloads and are therefore tightly coupled to server build configuration.

Risks: many arguments are parsed with `atoi`, so invalid numbers become zero. Several allocated `state.vop` objects are not freed because the process exits quickly. Query output exposes raw server pointers that are useful only diagnostically. Payload decoding proceeds after version/size mismatch warnings, so fields may be misleading across ABI-skewed builds. Commands can mutate live fileserver state and should not be treated as read-only except the query/stat paths.

Test signals: CLI tests should cover command registration/aliases, missing required arguments, DAFS prolog behavior, program type names and numeric override, reason override, all query printers with short/exact/oversized payloads, VGC operations, stats subcommands and help, and server-extension mismatch messages.
