## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_debugfs.c

### Purpose
`ivpu_debugfs.c` exposes ivpu debugfs files for BO listing, firmware identity and tracing, reset/recovery control, DVFS/profiling controls, dynamic clock throttling, hardware scheduler priority bands, and fault injection.

### Important APIs, Types, And Functions
Read-only show callbacks include `bo_list_show`, `fw_name_show`, `fw_version_show`, trace capability/config readers, boot mode and reset counters. Writable file ops update firmware dynamic debug, mark firmware logs read, drive profiling frequency, set trace masks/level via JSM, force recovery, reset/resume engines, configure DCT, and update HWS priority-band timings. `ivpu_debugfs_init()` registers the files.

### Control Flow
Initialization attaches standard DRM debugfs entries and custom files under the device root. Read paths pull data from `vdev`, firmware state, JSM queries, BO list, PM counters, or hardware counters. Write paths parse user input, mutate driver state, often send a JSM command or trigger PCI reset/recovery, and return the consumed byte count on success.

### State, Persistence, And Dependencies
Debugfs writes can persist in `vdev->fw` trace/DVFS fields, `vdev->hw->hws` priority-band arrays, PM DCT state, and hardware/firmware settings until reset or later writes. Dependencies include debugfs, DRM debugfs helpers, firmware log/JSM APIs, PM runtime/recovery, hardware helpers, and optional fault injection.

### Integration Points
This file is the main operator-facing diagnostic/control surface for the ivpu driver. It integrates with firmware trace configuration, DCT PM behavior, recovery work, hardware scheduler setup, and BO introspection.

### Risks
Several files are write-only control surfaces that can reset hardware or change scheduler timing. Trace config writes update cached driver state even if the JSM command fails because return values are not propagated. Priority-band parsing uses a compact text format and should reject partial input. Debug features are powerful and should remain gated by debugfs permissions/configuration.

### Test Signals
Mount debugfs and verify all files appear under the DRM device. Exercise reads, invalid writes, trace setting changes, `fw_log` mark-read behavior, `force_recovery`, DCT enable/disable on 40xx+, and priority-band updates with valid and invalid band IDs.
