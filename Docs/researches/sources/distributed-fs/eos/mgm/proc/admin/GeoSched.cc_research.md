# sources/distributed-fs/eos/mgm/proc/admin/GeoSched.cc

Purpose: Implements the legacy `geosched` admin command for inspecting and tuning the `GeoTreeEngine` placement scheduler.

Important APIs/types/functions: `ProcCommand::GeoSched()` handles `showtree`, `showsnapshot`, `showstate`, `showparam`, `set`, updater pause/resume, force refresh, disabled-branch add/remove/show, direct access geotag mapping, and proxygroup access mapping. Operations are delegated to `gOFS->mGeoTreeEngine`.

Control flow: Root is required. Show commands gather schedgroup, operation type, color, and monitoring flags before `printInfo()`. `set` parses parameter/index/value and saves through `setParameter(..., true)`. Disabled branch and access commands use `mSubCmd.beginswith()` to group related actions and pass `true` when changes should be saved to config.

State and persistence behavior: Scheduler parameters, disabled branches, access geotag mappings, and proxygroup mappings are persisted through `GeoTreeEngine` when called with save enabled. Pause/resume/force refresh are runtime scheduler-control actions. Output is accumulated in legacy `stdOut`/`stdErr` fields.

Dependencies and integration points: Depends on `ProcInterface`, `XrdMgmOfs`, and `GeoTreeEngine`. Group state changes in `GroupCmd` also manipulate disabled placement branches, so this file is part of the same placement-control surface.

Risks: Multiple independent `if` blocks rather than `else if` rely on non-overlapping subcommand names. Parameter parsing is thin and validation is delegated to the engine. Access mapping commands can persist broad changes such as clearing all direct mappings when geotag is `all`.

Test signals: Authorization, each show mode with monitoring/color flags, parameter set success/failure, pause failure path, force refresh, disabled branch add/remove/show persistence, direct and proxygroup access mapping set/clear/show, and ambiguous or unknown subcommand return code behavior.
