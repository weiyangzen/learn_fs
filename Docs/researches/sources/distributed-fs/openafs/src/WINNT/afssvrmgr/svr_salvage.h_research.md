# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_salvage.h

Purpose: declares the public interface and parameter packet for server/aggregate/fileset salvage operations in AFS Server Manager.

Important API/types: `SVR_SALVAGE_PARAMS` carries `LPIDENT lpiSalvage`, optional temp directory and log file buffers, concurrency count, and boolean salvager flags: force, readonly, inode logging, root inode logging, directory rebuild, and block-read mode. `Server_Salvage(LPIDENT lpi)` opens the modeless salvage UI for the selected identity.

Control flow contract: callers invoke `Server_Salvage` from command/menu handlers with a server, aggregate, or fileset identity. The UI fills this struct and passes it as `lpUser` to `taskSVR_SALVAGE`; `Task_Svr_Salvage` owns deletion after calling `AfsClass_Salvage`.

State and persistence: the struct is transient task input only. It stores fixed-size paths and flags but no persistent settings.

Dependencies/integration: depends on common AFS Manager types from `svrmgr.h`, especially `LPIDENT`, `MAX_PATH`, and task dispatch. Included by `svr_salvage.cpp` and `task.cpp`.

Risks/test signals: all path buffers must be populated with bounded `GetDlgItemText`; empty strings are interpreted later as `NULL`. Tests should verify that each UI option maps to the corresponding struct field and that ownership is never shared after dispatch.
