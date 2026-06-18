<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager_test.go

Purpose: validates CDI device resolution semantics against fixture specs.

Important APIs and types: `TestFindDevices` table-drives requests through `NewManager(cache, nil).FindDevices`.

Control flow: cases cover exact qualified device, first device of a kind when no name is supplied, wildcard all devices of a kind, class lookup across different CDI kinds, and erroring for a missing required device.

State and dependencies: each case creates a fresh CDI cache from `./fixtures`; no shared persistent state. Dependencies are BuildKit `pb.CDIDevice`, testify, and the CDI cache package.

Integration points: protects `Manager.parseDevice` behavior used by LLB execution device requests and entitlement validation.

Risks and test signals: tests use `ElementsMatch` for unordered multi-device results except the first-device case expects one exact device. They do not test optional missing devices, on-demand installers, auto-allow output, or OCI spec injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager_test.go -->
