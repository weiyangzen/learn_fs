# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_create.cpp

Purpose: Implements the Add Service property sheet for creating BOS-managed services on a selected server.

Important APIs/functions: `Services_Create` opens/focuses a singleton create sheet. `Services_Create_DlgProc` handles input changes and apply. `Services_Create_OnInitDialog` enumerates servers and fills common service names. `Services_Create_OnType` toggles fields for simple/cron services and populates recurrence days. `Services_Create_OnApply` collects fields into `SVC_CREATE_PARAMS` for `taskSVC_CREATE`. `Services_Create_EnableOK` validates required fields.

Control flow: The sheet is cached under `pcSVC_CREATE`. Server enumeration is async through `taskSVR_ENUM_TO_COMBOBOX`. Name changes call `Services_GuessLogName` and may auto-fill log filename. Type radio buttons enable run-now for simple services and recurrence day/time for cron services.

State and persistence: No direct persistence; it creates task packets for service creation. It reads no existing service state. The guessed log name is UI convenience.

Dependencies/integration: Depends on `svc_general.h` for log guesses, prop sheet cache, combobox helpers, time input helpers, and task dispatch.

Risks: `Services_Create_EnableOK` checks whether server combo is enabled, so OK may stay disabled if enum task failure leaves it disabled. Fields use `cchNAME` for command/params/log/notifier, which may truncate paths/commands longer than name length. Type handler references `IDC_SVC_TYPE_FS` in logic but the command switch only listens to simple/cron, so FS toggling must be covered by dialog resource behavior or may not update controls.

Test signals: Server enumeration success/failure, required name/command validation, log-name auto-fill, simple/cron/FS service types, cron day/time collection, and duplicate create sheet focus.
