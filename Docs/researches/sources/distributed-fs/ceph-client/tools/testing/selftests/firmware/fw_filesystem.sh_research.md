<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_filesystem.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_filesystem.sh

## Purpose
This script validates firmware loading from the filesystem, asynchronous requests, platform firmware requests, batched request paths, partial loads, not-found paths, and compressed firmware support.

## Important APIs, Types, And Functions
It uses config helpers such as `config_reset()`, `config_set_name()`, `config_set_into_buf()`, `config_set_partial()`, `config_set_sync_direct()`, `config_set_uevent()`, `config_trigger_sync()`, and `config_trigger_async()`. Readback helpers include `read_firmwares()`, `read_partial_firmwares()`, and `read_firmwares_expect_nofile()`. Test loops are driven by `do_tests()` and `test_request_firmware_compressed()`.

## Control Flow
After shared setup with a custom firmware path, it rejects empty names, verifies direct filesystem loading and async loading, optionally tests platform loading, then exercises batched request variants five times each with present, missing, and compressed firmware. Partial into-buffer requests validate offset/length slicing.

## State And Persistence
It changes `/sys/module/firmware_class/parameters/path`, writes many config knobs under `$DIR`, writes/readbacks `/dev/test_firmware` and `$DIR/read_firmware`, creates compressed firmware companions, and releases firmware between batched cases.

## Dependencies And Integration Points
The script depends on `test_firmware` sysfs control files, optional XZ/ZSTD compression tools and Kconfig support, optional platform trigger support, and `fw_lib.sh`.

## Risks
It assumes the test driver's sysfs ABI names are present; missing batched triggers cause skips. Compression tests depend on external tools. The readback comparison uses `diff -q -Z`, so whitespace behavior is intentionally tolerated.

## Test Signals
Pass signals include empty filename rejection, direct and async filesystem load success, platform load success when supported, nofile cases not hanging and not matching stale firmware, correct partial data, and success for both plain-preferred and compressed-only modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_filesystem.sh -->
