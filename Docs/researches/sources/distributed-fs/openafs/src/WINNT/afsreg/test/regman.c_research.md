# sources/distributed-fs/openafs/src/WINNT/afsreg/test/regman.c

## Purpose
Manual registry/service management utility for OpenAFS Windows configuration. It can list/add/delete vice partition table entries, get/set the server install directory, create/delete the BOS control service, and display installed client/server version information.

## Important APIs, Types, And Functions
Command handlers include `DoVptList`, `DoVptAdd`, `DoVptDel`, `DoDirGet`, `DoDirSet`, `DoBosCfg`, `DoBosDel`, and `DoVersionGet`. Setup functions register command syntaxes through the OpenAFS `cmd` package. `main` initializes the command error table, registers all syntaxes, and dispatches. It uses `vptab` APIs, `afssw` accessors, registry helpers, Windows Service Control Manager APIs, and OpenAFS path constants.

## Control Flow
VPT commands validate names/devices before reading or mutating Afstab entries. Directory commands read or write `AFSREG_SVR_SW_VERSION_DIR_VALUE`. BOS config either quotes an explicitly provided service path or constructs one from the server install dir and canonical server binary path, then calls `CreateService` for `TransarcAFSServer`. BOS delete opens and deletes the service, treating already-missing/marked-for-delete conditions as nonfatal. Version command attempts client and server version reads independently.

## State And Persistence
The utility mutates persistent registry state for server install directory and vice partition table entries, and mutates SCM service configuration when creating/deleting the BOS service. It reads installed version information and may allocate temporary strings that are freed by command handlers.

## Dependencies And Integration Points
It integrates the `afsreg`, `afssw`, and `vptab` libraries with the OpenAFS command parser and Windows SCM. It is useful as a pre-configuration-manager or diagnostic tool.

## Risks And Test Signals
Risks include destructive service deletion/creation, required administrator privileges, quoted path construction, mixed slash separators in the default BOS path, and unchecked `strcpy` into fixed-size `vptab` fields after validation. Test signals include each command against temporary registry/service fixtures, privilege-denied behavior, idempotent delete of missing service/partition, and version output when registry values are absent.
