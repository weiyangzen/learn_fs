# sources/cloud-native/cri-o/internal/version/linkmode_dynamic.go

Purpose: supplies the default link mode value for non-static builds.

Important APIs/types/functions: declares `const linkmode = "dynamic"` under build constraint `!static`.

Control flow: compile-time file selection only.

State and persistence: contributes to `version.Info.Linkmode` returned by `Get`; no persistent state.

Dependencies/integration: paired with `linkmode_static.go`; selected by Go build tags and consumed by `version.go`.

Risks: build tags must stay mutually exclusive or `linkmode` will be undefined/duplicated. Incorrect tag use affects version reporting only.

Test signals: version formatting tests use an explicit `Info` value, so build-tag coverage is mostly compile-time.
