# sources/distributed-fs/ceph-client/drivers/misc/mei/mei_dev.h

## Purpose
This header is the core private contract for the Intel MEI driver. It defines device, file-client, callback, DMA, firmware-status, power-gating, timeout, and hardware-operation abstractions shared by the ME/HECI, TXE, CSC, VSC, bus, interrupt, DMA-ring, debugfs, and userspace character-device layers.

## Important APIs, types, and functions
Key state enums are `file_state`, `mei_dev_state`, `mei_dev_pxp_mode`, `mei_dev_reset_to_pxp`, `mei_file_transaction_states`, `mei_cb_file_ops`, `mei_cl_io_mode`, `mei_pg_event`, and `mei_pg_state`. Core structures are `mei_device`, `mei_cl`, `mei_cl_cb`, `mei_cl_vtag`, `mei_me_client`, `mei_dma_data`, `mei_dma_dscr`, `mei_fw_status`, `mei_fw_version`, and `mei_dev_timeouts`. `struct mei_hw_ops` is the hardware vtable; inline wrappers such as `mei_hw_reset()`, `mei_hw_start()`, `mei_write_message()`, `mei_read_hdr()`, `mei_read_slots()`, and interrupt helpers dispatch through it. Public internal entry points include `mei_device_init()`, `mei_reset()`, `mei_start()`, `mei_restart()`, `mei_stop()`, `mei_register()`, `mei_deregister()`, IRQ handlers, DMA-ring helpers, and client-bus send/receive functions.

## Control flow and state
MEI operation is organized around `mei_device`: probe code allocates hardware-specific storage in flexible member `hw[]`, calls `mei_device_init()`, then `mei_register()` and `mei_start()`. Interrupt handlers use common read/write/completion queues while hardware-specific drivers supply readiness, reset, buffer, read, and write operations. Client file handles use `mei_cl` state, flow-control credits, wait queues, pending/completed read lists, and callback queues. Device progression is tracked by `dev_state`, `hbm_state`, power-gating events, reset counters, PXP setup state, and HBM capability bits.

## State and persistence behavior
All state is in-memory kernel state. Long-lived state includes opened client handles, ME firmware client inventory, HBM negotiated feature flags, wait queues, DMA descriptors, pending callbacks, timeout work, and client-bus device lists. There is no disk persistence; firmware state is queried through `fw_status` callbacks and rendered by `mei_fw_status_str()`.

## Dependencies and integration points
The header depends on Linux device, cdev, poll, MEI UAPI, and MEI client-bus APIs plus local `hw.h` and `hbm.h`. It is integrated by PCI drivers (`pci-me.c`, `pci-txe.c`, `pci-csc.c`), platform VSC transport, MEI bus clients, debugfs, DMA ring, HBM control, and userspace char-device layers. `kind_is_gsc()` and `kind_is_gscfi()` expose GSC/GSCFI classification for newer graphics security flows.

## Risks and test signals
Risk concentrates around lock ordering on `device_lock`, callback queue lifetime, state transitions during reset/suspend, DMA-ring bounds, HBM feature negotiation, and correct hardware vtable implementation. Test signals include successful probe/start/restart/remove on each hardware backend, sysfs firmware-status reads, client connect/disconnect, read/write flow-control stress, suspend/resume/runtime-PM cycles, reset storms capped by `MEI_MAX_CONSEC_RESET`, and debugfs visibility when enabled.
