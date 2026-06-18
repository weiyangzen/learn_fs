## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_drv.c

### Purpose
`ivpu_drv.c` is the main Intel NPU DRM accelerator PCI driver. It owns module parameters, per-user/per-file context lifetime, DRM ioctls, firmware boot/shutdown orchestration, PCI/IRQ setup, device initialization/finalization, probe/remove, and PM/error-handler registration.

### Important APIs, Types, And Functions
Module parameters include debug mask, optional test mode, PLL ratio bounds, scheduler mode, contiguous-page disable, and forced snoop. File/context APIs include `ivpu_file_priv_get()`, `ivpu_file_priv_put()`, `ivpu_open()`, `ivpu_postclose()`, and user-limit helpers. Public lifecycle APIs are `ivpu_boot()`, `ivpu_prepare_for_reset()`, and `ivpu_shutdown()`. IOCTL handlers include get/set param and BO/job/metric/cmdq/userptr registrations. Probe paths include `ivpu_pci_init()`, `ivpu_irq_init()`, `ivpu_dev_init()`, `ivpu_dev_fini()`, `ivpu_probe()`, and `ivpu_remove()`.

### Control Flow
Probe allocates a managed DRM device, initializes core structs and xarrays, maps BAR0/BAR4, sets DMA mask, allocates MSI/MSI-X, initializes hardware from buttress registers, powers up, initializes global/reserved MMU contexts, firmware, IPC, PM, boots firmware, enables job-done consumption and PM, then registers DRM/debugfs/sysfs. Open enforces per-UID context limits, allocates an SSID from `context_xa`, initializes an MMU context, and stores `file_priv`. Close cleans metric streamer state and releases the context asynchronously through krefs. Boot writes firmware boot params, starts firmware, waits for a boot IPC message, enables IRQ/IPCs, and initializes DCT/HWS on cold boot. Teardown aborts jobs, disables PM/recovery, disables IRQ/IPC/MMU, shuts down hardware, cleans contexts and BOs, and destroys xarrays.

### State, Persistence, And Dependencies
Persistent driver state is in `struct ivpu_device`, `struct ivpu_file_priv`, xarrays for contexts/doorbells/jobs, BO lists, PM/firmware/MMU/IPC substructures, module parameters, and PCI power state. Hardware state includes BAR mappings, DMA mask, MSI vector, power/D0i3 state, firmware execution, and MMU contexts. Dependencies include DRM accel/GEM/PRIME, PCI/MSI/PM runtime, firmware loading, ivpu MMU/FW/IPC/job/JSM/PM/sysfs/debugfs helpers, and UAPI `ivpu_accel.h`.

### Integration Points
This file binds the driver to PCI IDs for MTL, ARL, LNL, PTL-P, WCL, and NVL. It is the UAPI entry point for params, BOs, submissions, metric streamer, cmd queues, and userptr BOs. It coordinates hardware and firmware subsystems through the boot/shutdown and reset paths.

### Risks
Initialization order is strict because later firmware/IPC/MMU code needs powered hardware and mapped BOs. Error unwinds must destroy xarrays and free contexts exactly once. `pm_runtime_get_sync()` in file release must be balanced with autosuspend. Per-UID limits use kref counts, so leaks can deny future opens. Boot timeout or invalid boot message triggers diagnostics and coredump; missing flushes/workqueue drains during reset can race with IRQ work.

### Test Signals
Test probe/remove across all PCI IDs, open/close under per-user context limits, all param queries, boot timeout/coredump path, runtime/system suspend-resume, PCI reset callbacks, PRIME import/export restrictions, device unplug with open files, and error unwind by injecting failures at PCI, IRQ, HW, MMU, FW, IPC, and boot stages.
