# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/outline.go

Purpose: captures and renders outline subrequest information: build args, secrets, SSH mounts, target name/description, source bytes, and source locations.

Important APIs and types: `outlineCapture`, `argInfo`, `secretInfo`, `sshInfo`, `newOutlineCapture`, `clone`, `markAllUsed`, dispatch-state methods `args`, `secrets`, `ssh`, `Outline`, plus location helpers.

Control flow: captures are cloned per stage to inherit global ARG knowledge. Used args recursively mark dependencies. Rendering walks current stage, base stages, and dependency stages, deduplicates by visited maps, sorts by source location, and emits `outline.Outline`.

State and persistence: outline data is in-memory during conversion and returned through subrequest response.

Dependencies and integration: populated by ARG dispatch, secret/SSH mount dispatch, and `Dockerfile2Outline`; maps parser ranges to solver protobuf locations.

Risks and test signals: risks include missing dependency args, nil location comparison assumptions, duplicate suppression hiding redefinitions, and SSH slice preallocation typo using secrets length. Outline subrequest tests are relevant.
