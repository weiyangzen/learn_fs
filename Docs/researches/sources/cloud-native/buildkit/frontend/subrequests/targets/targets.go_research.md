<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/targets/targets.go -->
# sources/cloud-native/buildkit/frontend/subrequests/targets/targets.go

Purpose: defines the `frontend.targets` subrequest response for listing build targets/stages exposed by the current Dockerfile frontend.

Important APIs, types, and functions: `RequestTargets` and `SubrequestsTargetsDefinition` expose version `1.0.0` with `result.json` and `result.txt`. `List` contains `Targets []Target` and raw `Sources`. `Target` records name, default flag, description, base, platform, and optional source location. `List.ToResult` marshals JSON and text metadata. `PrintTargets` renders `TARGET DESCRIPTION`, labeling unnamed defaults as `(default)` and named defaults as `<name> (default)`.

Control flow and state: all work is pure serialization. Text rendering iterates target order as provided by the frontend and does not sort or filter.

Dependencies and integration: uses gateway client result metadata and solver protobuf locations. It is consumed by subrequest-aware clients that inspect Dockerfile stage inventories.

Risks and test signals: text output omits base, platform, source locations, and raw sources although JSON carries them. Tests should cover default label formatting and invalid JSON handling in `PrintTargets`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/targets/targets.go -->
