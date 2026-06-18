<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/protect_others.go -->
# sources/cloud-native/moby/internal/testutil/environment/protect_others.go

Purpose: non-Linux stub for default bridge protection so shared environment code compiles on Windows and other platforms. It defines an empty `defaultBridgeInfo`, a no-op `ProtectDefaultBridge`, and a no-op `restoreDefaultBridge`. Control flow and persistence are intentionally absent because non-Linux test hosts do not manage the Linux `docker0` bridge through this utility. Dependencies are only `context` and `testing`; integration is compile-time through build tags. Risks are low, but callers must not assume bridge restoration happened on non-Linux platforms. Test signal is build coverage across platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/environment/protect_others.go -->
