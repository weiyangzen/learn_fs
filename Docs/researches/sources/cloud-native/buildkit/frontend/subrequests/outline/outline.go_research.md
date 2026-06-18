<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/outline/outline.go -->
# sources/cloud-native/buildkit/frontend/subrequests/outline/outline.go

Purpose: defines the `frontend.outline` subrequest response for documenting build target parameters such as build args, secrets, SSH mounts, cache mounts, and source snippets.

Important APIs, types, and functions: `RequestSubrequestsOutline` and `SubrequestsOutlineDefinition` publish version `1.0.0`, the optional `target` parameter, and `result.json`/`result.txt` outputs. `Outline` is the top-level JSON structure. `Arg`, `Secret`, `SSH`, and `CacheMount` represent discovered parameters with optional `pb.Location`. `Outline.ToResult` emits formatted JSON and rendered text. `PrintOutline` renders target metadata plus BUILD ARG, SECRET, and SSH tables.

Control flow and state: the file is stateless. Rendering conditionally writes sections only when the corresponding data exists. `Name` defaults to `(default)` in text when the target has a description but no explicit name.

Dependencies and integration: integrates with gateway result metadata and protobuf source locations. Dockerfile frontend parsers populate the model, while buildctl or other clients consume the text and JSON outputs.

Risks and test signals: cache mount data is present in JSON but not printed in the current text renderer, which can surprise human-output users. `Sources` contains raw bytes and can enlarge metadata. Tests should assert JSON stability and text rendering for each non-empty section, including default target naming.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/outline/outline.go -->
