# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/sdsi/sdsi_test.py

## Purpose
Pytest suite for Intel SDSi auxiliary devices. It verifies driver loading, sysfs file presence, permissions, ownership, sizes, seek behavior, mailbox overflow handling, ENODEV after device removal, and optional kmemleak cleanliness.

## Important APIs, Types, And Functions
Globals discover sockets under `/sys/bus/auxiliary/devices/intel_vsec.sdsi.*`. Helpers are `read_bin_file()`, `get_dev_file_path()`, and `kmemleak_enabled()`. Test classes are `TestSDSiDriver`, `TestSDSiFilesClass`, `TestSDSiMailboxCmdsClass`, and `TestSdsiDriverLocksClass`. It uses `os.stat`, raw sysfs opens/writes, driver `unbind`, `modprobe`, and `/sys/kernel/debug/kmemleak`.

## Control Flow
Tests are parametrized across discovered socket indexes. File tests assert expected sysfs nodes, modes, root ownership, size contracts, no-seek writes for provisioning files, and seekable register reads. Mailbox tests write 1017 bytes to ensure `EOVERFLOW`. Lock/removal tests hold open provisioning fds, unbind the device, expect `ENODEV` on writes, reload underlying modules, and optionally scan kmemleak after removal.

## State And Persistence
The suite can unbind devices and unload/reload `intel_sdsi` and `intel_vsec`. It writes random bytes to provisioning nodes in negative tests and triggers kmemleak scans.

## Dependencies And Integration Points
Requires pytest, root-level sysfs access, Intel VSEC/SDSi hardware, auxiliary bus devices, driver bind/unbind sysfs, and optional kmemleak debugfs.

## Risks
`NUM_SOCKETS` is computed at import time, so module reloads during tests do not refresh parametrization. Lock/removal tests are invasive and can affect system device state. Provisioning writes must be rejected as expected to avoid changing hardware state.

## Test Signals
Signals are pytest assertions for exact modes, sizes, errno (`ESPIPE`, `EOVERFLOW`, `ENODEV`), successful driver reload, and zero-sized kmemleak report when enabled.
