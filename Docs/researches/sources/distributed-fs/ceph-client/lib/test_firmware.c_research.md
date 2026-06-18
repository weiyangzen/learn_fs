
# sources/distributed-fs/ceph-client/lib/test_firmware.c

## Purpose

This module exposes a misc device named `test_firmware` with sysfs attributes for exercising the firmware loader, fallback paths, batched synchronous/asynchronous requests, platform firmware lookup, and firmware upload support. It is a test harness for firmware APIs, not a production loader.

## Important APIs, Types, And Functions

The central state is `struct test_config`, protected by `test_fw_mutex`, containing firmware name, request mode, buffer sizing, partial-read settings, uevent behavior, batched request array, selected upload name, and `test_result`. `struct test_batched_req` tracks individual request completions, loaded firmware pointers, backing buffers, kthreads, and return codes. `struct test_firmware_upload` tracks registered upload endpoints, data buffers, cancel state, and injected upload errors.

The sysfs surface includes configuration attributes (`config_name`, `config_num_requests`, `config_into_buf`, `config_buf_size`, `config_file_offset`, `config_partial`, `config_sync_direct`, `config_send_uevent`, `config_read_fw_idx`, `config_upload_name`) and triggers (`trigger_request`, `trigger_async_request`, `trigger_custom_fallback`, optional `trigger_request_platform`, `trigger_batched_requests`, `trigger_batched_requests_async`, `release_all_firmware`, `read_firmware`, `upload_register`, `upload_unregister`, `upload_read`, `test_result`). The misc read path returns the currently loaded `test_firmware` data.

## Control Flow And State

Init allocates `test_fw_config`, initializes defaults (`test-firmware.bin`, four requests, 1 KiB buffer, uevents enabled), and registers the misc device with attribute groups. Synchronous triggers release stale firmware, request a named firmware object, and store it in `test_firmware`. Async triggers use `request_firmware_nowait()`, wait on `async_fw_done`, and rely on `trigger_async_request_cb()` to publish the firmware pointer.

Batched sync requests allocate a request array, launch one kthread per request, then wait for completions while leaving firmware objects retained until explicit release. Batched async requests submit multiple `request_firmware_nowait()` calls, use completions from callbacks, and preserve results for later `read_firmware`. Upload registration creates firmware upload endpoints using `firmware_upload_register()` and `upload_test_ops`; writes are copied in 37-byte chunks and may inject failures at preparing, transferring, or programming stages.

## Dependencies And Integration Points

The module depends on firmware loader APIs (`request_firmware*`, `release_firmware`, `firmware_upload_register`), miscdevice/sysfs infrastructure, kthreads, completions, vmalloc, uaccess helpers, optional EFI embedded firmware state, and the `TEST_FIRMWARE` namespace. Userspace selftests usually drive the sysfs attributes and read the misc device.

## Risks And Test Signals

This file intentionally tests races and lifetime boundaries, including freeing the firmware name immediately after async submission. Risks include stale global completion state, retained firmware objects when `release_all_firmware` is not called, config changes while batched requests exist, and keeping `fw_upload_err_str` synchronized with firmware upload internals. Signals include sysfs return codes, `test_result`, misc-device read data, `read_firmware` contents, upload data returned by `upload_read`, and kernel logs for loaded sizes and injected errors.
