# sources/distributed-fs/beegfs-go/common/rst/flags.go

Purpose: centralizes CLI flag-name constants used in RST error messages and command wiring.

Important constants are `AllowRestoreFlag`, `PriorityFlag`, `RemotePathFlag`, `RemoteTargetFlag`, `StorageClassFlag`, and `UpdateFlag`.

Control flow and state are absent. The constants are read by RST helpers to produce consistent messages such as missing `--remote-target`, missing `--remote-path`, or requiring `--allow-restore`.

Dependencies: none. Integration points include RST job request preparation, S3 archive restore checks, and CTL commands that define matching flags.

Risks: these strings are user-facing CLI contracts. Renaming a constant value without updating cobra command definitions would create misleading error messages. Adding new RST flags should use this file to avoid drift.

Test signals: no direct tests. Error-message assertions elsewhere may indirectly depend on these values.
