# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_drv.h

## Purpose
`bfad_drv.h` is the central BFAD driver definition header. It declares compile-time constants, driver flags, core objects for PCI functions/ports/vports/VFs, DMA buffers, FCXP pass-through context, completion wrappers, logging, module parameters, and cross-file driver prototypes.

## Important APIs, Types, and Functions
Key macros include `BFAD_DRIVER_NAME`, `BFAD_DRIVER_VERSION`, `BFAD_IRQ_FLAGS`, state flags such as `BFAD_HAL_INIT_DONE`, `BFAD_DRV_INIT_DONE`, `BFAD_PORT_ONLINE`, `BFAD_FC4_PROBE_DONE`, `BFAD_EEH_BUSY`, and defaults such as `BFAD_LUN_QUEUE_DEPTH`, `BFAD_IO_MAX_SGE`, `BFAD_MIN_SECTORS`, and `BFAD_MAX_SECTORS`. `struct bfad_s` is the root PCI-function object and owns the BFA HAL, FCS fabric, PCI resources, completions, locks, primary port, configuration, MSI-X table, timer, IM module, trace/log buffers, debugfs state, AEN queues, and vport list. `struct bfad_port_s`, `bfad_vport_s`, and `bfad_vf_s` represent physical/virtual FC constructs. `struct bfad_fcxp` carries FC pass-through request/response DMA state. `struct bfad_hal_comp` wraps asynchronous BFA completions. The header prototypes PCI lifecycle, interrupt setup, HAL memory management, port/vport creation, debugfs, timer, and worker functions.

## Control Flow
There is no executable flow in the header, but its types encode the driver lifecycle: PCI probe allocates/configures `bfad_s`, initializes BFA/FCS, configures the physical port, creates IM/SCSI state, starts interrupts/timers/workers, and later tears them down through the declared stop/remove/uninit helpers. Shared fields and flags coordinate transitions across implementation files.

## State and Persistence
Most persistent in-memory state for a BFAD instance lives in `struct bfad_s`: hardware mappings, adapter names, firmware config, link stats, debug buffers, AEN queues, and vport lists. `bfad_cfg_param_s` stores runtime queue and binding configuration. Persistent hardware/flash state is not stored here directly but is reached through BFA modules referenced by `bfad_s`.

## Dependencies and Integration Points
The header integrates Linux PCI, DMA, interrupts, cdev/fs, timers, workqueues, SCSI, FC transport, BSG, and BFA/FCS headers. It is included by the sysfs, IM, debugfs, and BSG files in this work item and likely by PCI/core implementation files outside it.

## Risks
Many flags share one `u32` field, and `BFAD_PORT_DELETE` reuses bit value `0x1` in port-level flags while `BFAD_MSIX_ON` uses the same bit in `bfad_flags`; this is safe only because the fields differ. The root structure is large and shared across interrupt, workqueue, sysfs, BSG, and SCSI contexts, so lock discipline around `bfad_lock`, `bfad_mutex`, and AEN spinlock is critical. External module parameters can alter queue sizes and transfer limits, so bounds must be validated in code using them.

## Test Signals
Build tests should catch include-order and type drift. Runtime tests should cover PCI probe/remove, MSI-X and INTx paths, EEH flags, debugfs enable/disable, vport lists, AEN queue reuse, and BSG FCXP allocation paths that depend on `struct bfad_fcxp`.
