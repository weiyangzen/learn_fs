# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst.c

## Purpose
This is the common low-level Intel SST core for Atom HiFi2 platforms. It implements Merrifield-style interrupt handling, driver operation selection, context initialization and cleanup, asynchronous firmware request startup, sysfs firmware-version reporting, runtime/system PM, and DSP memory save/restore across suspend.

## Important APIs, types, and functions
Interrupt handling is split between `intel_sst_interrupt_mrfld()` and `intel_sst_irq_thread_mrfld()`. The Merrifield operation table `mrfld_ops` wires interrupt, reset, start, post-message, process-reply, save-context, allocate-stream, and post-download callbacks. Public lifecycle helpers are `sst_driver_ops()`, `sst_alloc_drv_context()`, `sst_context_init()`, `sst_context_cleanup()`, and `sst_configure_runtime_pm()`. PM paths are `intel_sst_runtime_suspend()`, `intel_sst_suspend()`, and `intel_sst_resume()`, exported through `intel_sst_pm`.

## Control flow
Bus-specific probe code allocates a context, fills platform data/resources, and calls `sst_context_init()`. Initialization selects operation callbacks, initializes locks/lists/workqueue, sets stream state, requests the threaded IRQ, masks default interrupts, adds a CPU latency QoS request, starts asynchronous firmware caching, creates the firmware-version sysfs group, and registers the DSP with the ASoC platform. Hard IRQ acknowledges done interrupts and queues pending IPC post work; busy interrupts copy large payloads from the mailbox, enqueue `ipc_post` objects on `rx_list`, clear DSP interrupt state, and wake the threaded handler. The thread drains `rx_list` and dispatches async process messages or command replies.

## State and persistence behavior
The `intel_sst_drv` context owns global firmware state, stream contexts, IPC queues, block waiters, memory mappings, workqueue, QoS request, and cached firmware. Firmware version is exposed through sysfs. Suspend can snapshot IRAM, DRAM, SRAM/mailbox, and DDR into `struct sst_fw_save`, then restore those memories and restart firmware on resume. Runtime suspend only prepares firmware for D3 and resets the DSP.

## Dependencies and integration points
The file depends on Linux IRQ, firmware, PM runtime, PM QoS, ACPI, sysfs, ASoC, and the platform registration API in `sst-mfld-platform.h`. It coordinates helper implementations in `sst_ipc.c`, `sst_loader.c`, `sst_stream.c`, `sst_pvt.c`, and bus probes.

## Risks and edge cases
The interrupt path must handle invalid mailbox sizes and allocation failure in atomic context. `sst_context_init()` requests firmware asynchronously before actual runtime load, so callers must tolerate firmware not being cached yet. Suspend rejects running streams and optionally frees streams when platform data says streams are lost. Memory snapshot sizes use base/end fields and must match mapped ranges. Error handling around sysfs group creation removes a group that may not have been created.

## Test signals
Probe logs, IRQ registration, firmware async request, sysfs `firmware_version`, IPC done/busy interrupt behavior, runtime autosuspend, system suspend/resume with idle streams, stream reallocation after resume on Baytrail, and negative tests for missing firmware, IRQ failures, mailbox-size corruption, and active stream suspend rejection are high-value signals.
