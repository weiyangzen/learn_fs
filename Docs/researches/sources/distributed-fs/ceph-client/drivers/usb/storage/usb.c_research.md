# sources/distributed-fs/ceph-client/drivers/usb/storage/usb.c

## Purpose

`usb.c` is the main driver body for classic USB Mass Storage. It owns module parameters, device matching metadata, probe/unbind, SCSI host allocation, the per-device command thread, delayed scanning, suspend/resume/reset hooks, quirk parsing, and integration with UAS fallback.

## Important APIs, Types, and Functions

Module parameters are `delay_use` and `quirks`. Probe helpers include `usb_stor_probe1()`, `usb_stor_probe2()`, `storage_probe()`, `associate_dev()`, `get_device_info()`, `get_transport()`, `get_protocol()`, `get_pipes()`, and `usb_stor_acquire_resources()`. Runtime functions include `usb_stor_control_thread()`, `usb_stor_scan_dwork()`, `fill_inquiry_response()`, `usb_stor_adjust_quirks()`, `usb_stor_disconnect()`, `quiesce_and_remove_host()`, `release_everything()`, and PM/reset hooks `usb_stor_suspend()`, `usb_stor_resume()`, `usb_stor_reset_resume()`, `usb_stor_pre_reset()`, and `usb_stor_post_reset()`.

## Control Flow

`storage_probe()` first lets UAS claim viable devices and lets specialized subdrivers claim devices from the usual ignore table. It then maps the matched USB ID to the parallel unusual-device metadata table, calls `usb_stor_probe1()` to allocate and initialize `struct us_data`, and calls `usb_stor_probe2()` to validate transport/protocol, find endpoints, acquire URB/control-thread resources, add the SCSI host, and schedule delayed scanning after `delay_use`.

The control thread sleeps on `cmnd_ready`, takes `dev_mutex`, validates target/LUN/data direction, fakes INQUIRY for `US_FL_FIX_INQUIRY`, otherwise calls the selected protocol handler, then releases locks and completes the SCSI command. Scanning optionally sends GetMaxLUN for BOT, raises host max_lun for large LUN counts, calls `scsi_scan_host()`, and balances runtime PM. Disconnect cancels scanning, removes the SCSI host, sets disconnect flags, wakes reset waits, stops the control thread, calls subdriver destructors, frees DMA buffers/URB/control request, and drops the SCSI host reference.

## State and Persistence Behavior

Long-lived state is per-device `struct us_data`: USB pointers, unusual metadata, quirk flags, dynamic flags, endpoint pipes, transport/protocol function pointers, SCSI command pointer, control thread, coherent I/O buffer, control request, current URB/SG request, completions, delayed scan work, subdriver private data, and last-sector hack counters. `delay_use` and `quirks` are module parameters exposed through sysfs. There is no file persistence, but probe changes USB interface state, runtime PM references, SCSI hosts, and block devices.

## Dependencies and Integration Points

The file depends on USB core, SCSI midlayer, workqueues, kthreads, runtime PM, unusual device tables, transport/protocol/scsiglue helpers, optional UAS detection, and subdriver initializer headers. It exports common probe/disconnect/PM helpers for usb-storage subdrivers.

## Risks and Edge Cases

The `usb_storage_usb_ids[]` and `us_unusual_dev_list[]` arrays must remain line-for-line aligned. `quirks=` parsing can override important flags and ignore unrecognized characters silently. The control thread uses a single outstanding `us->srb`, guarded by host lock and `dev_mutex`; abort and reset paths rely on dynamic flags being cleared in the right order. Highmem hosts without DMA/local-memory support are rejected because the driver does not bounce or kmap buffers. Delayed scan cancellation must balance autopm references.

## Test Signals

Test normal BOT devices, UAS-capable fallback, ignored specialized devices, dynamic IDs, quirk parameter parsing, fixed inquiry, invalid target/LUN rejection, delayed scan and scan cancellation, GetMaxLUN behavior, suspend/resume/reset hooks, disconnect during scan and active I/O, highmem/non-DMA host rejection, and subdriver initializer/destructor lifetimes.
