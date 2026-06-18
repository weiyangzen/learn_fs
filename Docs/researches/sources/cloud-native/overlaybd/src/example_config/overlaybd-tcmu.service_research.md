<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd-tcmu.service -->
# sources/cloud-native/overlaybd/src/example_config/overlaybd-tcmu.service

Purpose: systemd unit for the OverlayBD TCMU daemon.

APIs and control flow: Loads `target_core_user` before start, runs `/opt/overlaybd/bin/overlaybd-tcmu`, restarts always, raises NOFILE, preserves core dumps, and keeps the process alive independently of shutdown ordering.

State and persistence: systemd owns restart state; daemon writes logs and configfs state separately.

Dependencies and integration: Installed by CMake and enabled in CI. Requires root privileges and kernel target_core_user support.

Risks and test signals: `KillMode=process` may leave child/thread cleanup to daemon behavior. Validation is `systemctl start/status` and successful configfs device creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/overlaybd-tcmu.service -->
