<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/afscfg.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/afscfg.h

Purpose: Central application header for the AFS server configuration UI. It declares wizard step IDs, configuration-state flags, size limits, the `CFG_DATA` state structure, global handles, logging objects, and string accessor APIs.

Important APIs/types/functions: `StateID` enumerates the twelve wizard pages. `CONFIG_STATE` combines mutually exclusive states (`CS_NULL`, `CS_DONT_CONFIGURE`, `CS_CONFIGURE`, `CS_ALREADY_CONFIGURED`, `CS_UNCONFIGURE`) with the `CS_DISABLED` flag. `CFG_DATA` stores all choices and discovered state: server roles, root volume IDs/existence/replication flags, partition selection, system-control machine, cell/admin credentials, local and client host/cell information, reuse/login flags, and salvage thread/log state. The header declares `WizStep_Common_DlgProc`, `QueryCancelWiz`, `GetLibHandles`, `GetHandles`, and TCHAR/ANSI accessors.

Control flow: No runtime implementation, but it defines the shared contract every page follows: pages mutate `g_CfgData` state bits and text fields, and the final configuration page consumes them to assemble executable steps.

State and persistence: `CFG_DATA` is process-local and centralizes transient wizard/config-manager state. Some fields mirror durable AFS state discovered or written by cfg/vos/bos APIs, but the struct itself is not persisted. Admin and server passwords are kept in memory.

Dependencies and integration points: Includes OpenAFS cfg/util admin headers, `WINNT/afsapplib`, TCHAR/CRT debug support, hourglass/toolbox/logging/conversion/validation helpers, and `cfg_utils.h` after `CONFIG_STATE` is defined.

Risks: All modules share one global mutable state object with no ownership boundaries. Fixed-size credential and name buffers can truncate inputs. The state constants are integer flags, so equality checks can accidentally ignore or mishandle `CS_DISABLED` when combined with another state.

Test signals: Compile all pages against this contract; verify each page updates the expected `CFG_DATA` fields; test disabled-state combinations; validate boundary-length cell, machine, partition, admin, and password values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/afscfg.h -->
