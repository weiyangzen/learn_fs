# sources/distributed-fs/openafs/src/vol/fssync.h

Purpose: public protocol and API contract for fileserver synchronization over the generic SYNC layer. It defines the FSSYNC protocol version, command/reason codes, payload structures, endpoint constants, and client/server prototypes.

Important APIs/types/functions: `FSYNC_PROTO_VERSION` is 3. `enum FSYNCOpCode` defines volume lifecycle operations (`FSYNC_VOL_ON`, `OFF`, `NEEDVOLUME`, `DONE`, `ATTACH`, `LEAVE_OFF`, `FORCE_ERROR`), volume queries (`QUERY`, `QUERY_HDR`, `QUERY_VOP`, `QUERY_VNODE`), callback/move/list commands, statistics commands, and DAFS volume group cache commands (`FSYNC_VG_QUERY`, `ADD`, `DEL`, `SCAN`, `SCAN_ALL`). `enum FSYNCReasonCode` names operational reasons and denial causes such as salvage, move, exclusive checkout, unknown volume, wrong partition, bad state, and partition scanning. Payload types include `offlineInfo`, `FSSYNC_VolOp_hdr`, `FSSYNC_VolOp_command`, `FSSYNC_VolOp_info`, `FSSYNC_StatsOp_hdr`, `FSSYNC_VnQry_hdr`, `FSSYNC_VGQry_response_t`, and `FSSYNC_VGUpdate_command_t`.

Control flow: callers use the client prototypes to initialize a connection, send a generic operation or typed volume/stat/VGC operation, and disconnect. The fileserver calls `FSYNC_fsInit` to start the server side. `FSYNC_VerifyCheckout` is part of the checkout-lock verification flow for DAFS utilities.

State and persistence: the header declares state-bearing wire payloads but owns no storage. `FSSYNC_VolOp_info` is important persistent in-memory metadata attached to `Volume` objects while an external volume operation is pending.

Dependencies: includes `voldefs.h` and depends on `daemon_com.h` symbols being available to command/reason code macros and command/response header pointer types. Volume ids and volume group limits come from OpenAFS volume headers.

Integration points: shared by client, server, debug utility, volume utilities, salvagers, and VGC code. Endpoint constants bind FSSYNC to port 2040 or `fssync.sock` depending on socket mode.

Risks: fixed-size `partName[16]` is a protocol limit and must be null-validated by receivers. Adding opcodes requires updating documentation, stringification in `fssync_inline.h`, client wrappers if needed, server dispatch, and debug support. Struct layout is the local ABI between processes.

Test signals: compile/link all declared APIs under client/server build flags, check every opcode/reason maps to expected values above the SYNC user base, validate payload sizes against `SYNC_PROTO_MAX_LEN`, and verify all server/client/debug switch statements handle newly added opcodes.
