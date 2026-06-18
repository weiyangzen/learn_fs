# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_base.c

## Purpose
Core GenWQE PCI driver implementation. It owns module initialization, PCI probe/remove, BAR/DMA setup, card start/stop, character-device creation orchestration, health monitoring, fatal error recovery, FFDC buffer allocation, SR-IOV configuration, and PCI error handling.

## Important APIs, Types, And Functions
Global state includes `genwqe_devices[]`, the GenWQE class, and debugfs root. Key functions are `genwqe_dev_alloc/free()`, `genwqe_pci_setup/remove()`, `genwqe_start/stop()`, `genwqe_recover_card()`, `genwqe_health_thread()`, `genwqe_fir_checking()`, `genwqe_bus_reset()`, `genwqe_platform_recovery()`, `genwqe_reload_bistream()`, PCI error callbacks, `genwqe_sriov_configure()`, and module init/exit.

## Control Flow
Module init registers the class, creates debugfs root, and registers the PCI driver. Probe initializes CRC support, allocates a card slot, enables PCI memory, requests BARs, sets DMA mask, maps BAR0, reads hardware IDs, starts service-layer queues, applies hardware tweaks, configures PF/VF job timers, creates the char device, and starts the health thread for privileged functions. Stop tears down queues, device nodes, service layer, SR-IOV, and FFDC. The health thread periodically reads GFIR and unit registers, logs/clears informational FIRs, recovers fatal conditions via bus reset or platform recovery, and handles requested bitstream reload.

## State, Persistence, And Dependencies
Driver state is `struct genwqe_dev`: card index, state, MMIO pointer, cached unit IDs, FFDC buffers, queue and health threads, device/class/cdev data, debugfs, VF timeout settings, open-file list, and recovery knobs. Persistent hardware state includes card bitstream, FIR/GFIR registers, queues, and PCI function state. Dependencies include PCI core, DMA API, kthreads, wait queues, debugfs, class/cdev helpers from sibling files, service-layer/DDCB code, and architecture PCI error recovery.

## Integration Points
The PCI ID table covers IBM GenWQE PF/VF variants. Internal calls integrate with `card_dev.c`, `card_ddcb.c`, `card_sysfs.c`, `card_debugfs.c`, and `card_utils.c`. Kconfig controls platform recovery. Userspace observes device creation/removal under the GenWQE class and debugfs tuning/diagnostic files.

## Risks
Recovery paths deliberately tear down and recreate devices while open files may exist, so async notification and forced close behavior in sibling code is critical. Health monitoring uses raw MMIO and must distinguish fatal `IO_ILLEGAL_VALUE` from informational FIRs. Bus reset temporarily unmaps BARs and assumes later remapping succeeds. SR-IOV and PF/VF privilege detection depend on hardware register accessibility. The device node default mode is `0666`, making userspace ABI hardening important.

## Test Signals
Test PCI probe/remove, DMA32 fallback, BAR mapping failure, nonprivileged VF operation, PF health-thread recovery, injected hardware/bus/GFIR failures, platform recovery enabled/disabled, PCI AER callbacks, SR-IOV enable/disable, bitstream reload request, FFDC allocation failures, and repeated stop after failed recovery.
