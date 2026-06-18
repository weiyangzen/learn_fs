# sources/distributed-fs/openafs/src/vol/fssync_inline.h

Purpose: diagnostic stringification for FSSYNC command and reason codes. It complements `daemon_com_inline.h` by covering protocol-specific values.

Important APIs/types/functions: `FSYNC_com2string(afs_int32 command)` returns names for `SYNC_COM_CHANNEL_CLOSE` and every `FSYNC_*` command currently declared in `fssync.h`. `FSYNC_reason2string(afs_int32 reason)` returns names for generic SYNC reasons plus FSSYNC reasons from `FSYNC_WHATEVER` through `FSYNC_PART_SCANNING`. Unknown values return `"**UNKNOWN**"`.

Control flow: both functions are inline switch statements with macro-generated cases.

State and persistence: no mutable state or persistence. Returned values are string literals.

Dependencies: includes `fssync.h`; callers normally include OpenAFS headers that define `static_inline` and integer types.

Integration points: used in server verbose logging and debug tool output. It is the main human-readable bridge for FSSYNC packet traces.

Risks: the command table must be kept in sync with `enum FSYNCOpCode`, and the reason table should include generic and protocol-specific reason values. It currently omits `SYNC_REASON_PAYLOAD_TOO_BIG`, so that generic reason will display as unknown. Return type is mutable `char *` despite literals.

Test signals: assert every command/reason in `fssync.h` stringifies as expected, include at least one generic SYNC reason, and check unknown numeric values.
