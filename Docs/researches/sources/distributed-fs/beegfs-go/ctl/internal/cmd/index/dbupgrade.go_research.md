
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/dbupgrade.go

- Purpose: defines a currently disabled/unused Hive Index database upgrade command.
- Important APIs: `newGenericUpgradeCmd`, `newUpgradeCmd`, and `runPythonUpgradeIndex`, retained via blank identifier assignments.
- Control flow/state: checks package config, wraps db flags, injects `-n <numWorkers>`, and runs `bee db`.
- Dependencies/integration: uses Viper worker config, `bflag`, logger, and external Hive Index database utilities.
- Risks/tests: upgrade/downgrade/delete/restore operations are persistent database mutations; the command appears intentionally not registered in `index.go`, reducing accidental exposure. No direct tests.
