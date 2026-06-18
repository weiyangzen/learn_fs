# sources/distributed-fs/openafs/src/bubasics/bubasics.h

`bubasics.h` defines common backup-system constants, version numbers, ports, name lengths, dump result states, expiration encodings, tape-name helper macros, a double-linked queue node type, queue invariants, and the shared `statusS` task-status structure.

Important types and macros include `BUTM_MAJORVERSION`, `CUR_BUTC_VERSION`, `CUR_TAPE_VERSION`, backup database magic/version constants, `BC_MESSAGEPORT`, `BC_TAPEPORT`, `AFSCONF_BUDBPORT`, dump result codes, `BU_MAX*` sizing constants, `NEVERDATE`/`cTIME`, `tc_MakeTapeName`, `struct dlqlink`, `DLQ_*` types, task flags such as `STARTING`, `ABORT_REQUEST`, `TASK_DONE`, `CONTACT_LOST`, `TASK_ERROR`, and `struct statusS`/`statusP`.

There is no executable control flow, but the header governs binary and wire compatibility across backup coordinator, tape coordinator, backup database, and tape modules. State represented here includes queued task status, dump progress counters, current volume name, scheduled command line, and job metadata.

Dependencies are OpenAFS integer types and `ctime` consumers; queue function prototypes are implemented elsewhere. Risks include fixed-width name buffers, macro side effects (`tc_MakeTapeName`, `cTIME`), legacy version constants that must not change casually, typo-prone flag semantics shared between client/server, and `statusS` ownership of `cmdLine`. Test signals are compile coverage across backup components, queue invariant tests, and status flag interop between bucoord and butc.
