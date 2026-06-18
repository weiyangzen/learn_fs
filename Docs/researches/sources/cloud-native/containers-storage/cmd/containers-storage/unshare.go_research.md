<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/unshare.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/unshare.go

- Purpose: Runs a command inside a user namespace through the containers/storage unshare helper.
- Important behavior: `unshareFn` delegates to namespace reexecution/command execution.
- Control flow and state: May reexec process with user namespace mappings and then run requested arguments.
- Dependencies and integration: Uses `pkg/unshare` and common CLI dispatch.
- Risks: Namespace behavior differs by kernel/subuid/subgid setup; nested unshare can confuse scripts.
- Test signals: Rootless CLI workflows and namespace-sensitive integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/unshare.go -->
