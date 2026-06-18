# sources/control-plane/rook/pkg/daemon/ceph/client/osd_test.go

Purpose: validates selected OSD query and maintenance helpers.

Important test cases: `TestHostTree` parses a fake OSD tree and checks invalid JSON behavior. `TestOsdListNum` parses OSD ID lists and invalid JSON. `TestOSDDeviceClasses` uses fake device class output and verifies both success and error paths. `TestConvertKibibytesToTebibytes` verifies conversion for 1024 KiB and 1 TiB in KiB. `TestOSDOkToStop` covers successful ok-to-stop output, command failure for unsafe OSDs, and `maxReturned=0` pass-through.

Control flow and dependencies: tests use `exectest.MockExecutor`, `AdminTestClusterInfo()`, fake OSD helpers, and Ceph version constants. They capture `seenArgs` to validate `osd ok-to-stop <id> --max=<n>`.

Risks and coverage gaps: the tests do not cover `OSDDump.StatusByID()`, flag setting/unsetting, `GetOSDUsage()`, `ResizeOsdCrushWeight()`, `SetDeviceClass()`, `OsdSafeToDestroy()`, `SetPrimaryAffinity()`, metadata, or blocklist behavior. Existing tests give useful signals for JSON decoding and command shape, but OSD mutation paths remain higher risk due to limited coverage.
