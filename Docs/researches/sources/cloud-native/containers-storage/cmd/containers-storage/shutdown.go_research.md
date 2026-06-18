<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/shutdown.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/shutdown.go

- Purpose: Exposes store shutdown behavior from the CLI.
- Important behavior: `forceShutdown` flag controls whether shutdown should be forced.
- Control flow and state: Calls store shutdown API, which may release resources, unmount, or close driver state depending on backend.
- Dependencies and integration: Uses storage store lifecycle API.
- Risks: Forced shutdown can interrupt active users of the same store.
- Test signals: Store can be reopened cleanly after shutdown.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/shutdown.go -->
