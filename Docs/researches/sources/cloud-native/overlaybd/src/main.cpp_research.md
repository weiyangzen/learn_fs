<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/main.cpp -->
# sources/cloud-native/overlaybd/src/main.cpp

Purpose: `overlaybd-tcmu` daemon entry point and SCSI command bridge from kernel TCMU devices to `ImageFile` operations.

APIs and control flow: Initializes Photon, signals, image service, rlimit, and TCMU netlink block/reset. Registers TCMU handler subtype `overlaybd`. `dev_open` parses `dev_config=overlaybd/<config>[;<dev_id>]`, creates an image file, sets TCMU capacity/write-protect, and starts per-device event loop. `TCMULoop` watches the master fd; `TCMUDevLoop` reads commands and dispatches through a Photon thread pool. `cmd_handler` emulates inquiry/capacity/mode commands, maps READ to retried `preadv`, WRITE to `pwritev`, sync to `fdatasync`, and WRITE SAME unmap to `fallocate`.

State and persistence: Holds global `imgservice`, main loop, per-device `obd_dev`, configfs device state, inflight counts, and thread objects.

Dependencies and integration: libtcmu, SCSI headers, Photon event loop/thread pool, systemd unit, kernel target_core_user.

Risks and test signals: `sure` can retry for seven days, masking stuck IO. Netlink buffer tuning requires privileges. E2E configfs mount/read/write-protect tests are essential.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/main.cpp -->
