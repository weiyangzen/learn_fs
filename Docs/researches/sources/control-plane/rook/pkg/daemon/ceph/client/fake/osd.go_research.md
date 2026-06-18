# sources/control-plane/rook/pkg/daemon/ceph/client/fake/osd.go

Purpose: provides deterministic fake Ceph OSD JSON strings for unit tests in the client package and related operator code.

Important APIs: `OsdLsOutput(numOSDs)` returns JSON for `ceph osd ls` with IDs from 0 to `numOSDs-1`. `OsdTreeOutput(numNodes, numOSDsPerNode)` returns a simple CRUSH tree with one root, host nodes, and OSD leaves. `OsdOkToStopOutput(queriedID, returnOsdIds)` returns success or failure-shaped JSON for `ceph osd ok-to-stop`. `OSDDeviceClassOutput(osdId)` returns device-class JSON for a single OSD or a fake error string when no ID is provided.

Control flow and state: all functions are pure string renderers. `OsdTreeOutput()` uses negative host IDs beginning at -3 and assigns OSD IDs as `n + 3*i`, which creates a predictable distribution for the documented 3-OSDs-per-node example but is less general if callers expect sequential IDs for other `numOSDsPerNode` values.

Dependencies and integration: used by `osd_test.go` and can be reused by tests needing plausible Ceph JSON without embedding long fixtures. Risks include hand-rendered JSON drifting from real Ceph schemas and limited modeling of complex CRUSH layouts, stray OSDs, non-HDD device classes, down/out states, and non-default roots. Tests consume these helpers for OSD list, tree, ok-to-stop, and device class scenarios.
