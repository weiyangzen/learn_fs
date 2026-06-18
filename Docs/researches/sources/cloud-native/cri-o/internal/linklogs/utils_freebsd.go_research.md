# sources/cloud-native/cri-o/internal/linklogs/utils_freebsd.go

Purpose: FreeBSD implementation of linked-log platform helpers. `mountLogPath` and `unmountLogPath` both return explicit unsupported errors. There is no state mutation or persistence because no mount operation is attempted. Integration is selected by `freebsd` build tag and used by `MountPodLogs`/`UnmountPodLogs`. Risks are feature unavailability on FreeBSD and callers surfacing unsupported errors when linked logs are configured. Test signals are compile-time separation and any platform-specific error handling tests.
