<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_unix.go -->
# sources/cloud-native/moby/pkg/plugins/discovery_unix.go

Purpose: Unix implementation of plugin spec search paths. It chooses rootless paths under XDG config/lib homes when `ROOTLESSKIT_STATE_DIR` is set, otherwise `/etc/docker/plugins` and `/usr/lib/docker/plugins`. State is environment-derived. Dependencies include `homedir` and filesystem path joining. Risks include a likely fallback subtlety in `rootlessConfigPluginsPath` where the error branch uses `configHome`, rootless env detection by variable only, and path existence/permission differences. Test signal is rootless/discovery behavior through Unix tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_unix.go -->
