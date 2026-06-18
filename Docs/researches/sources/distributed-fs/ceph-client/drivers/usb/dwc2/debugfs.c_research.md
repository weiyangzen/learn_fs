<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/debugfs.c

## Purpose
`debugfs.c` creates DWC2 debugfs observability and limited gadget test-mode control. It exposes current parameters, hardware parameters, requested `dr_mode`, register dumps, gadget state, FIFO layout, endpoint queues, and test mode selection.

## Important APIs, types, and functions
The public functions are `dwc2_debugfs_init` and `dwc2_debugfs_exit`. Gadget-capable helpers include `testmode_write`, `testmode_show`, `state_show`, `fifo_show`, `ep_show`, and `dwc2_hsotg_create_debug`. Common debugfs helpers include the large `dwc2_regs` `debugfs_reg32` table, `params_show`, `hw_params_show`, and `dr_mode_show`. File operations are generated through `DEFINE_SHOW_ATTRIBUTE` or custom `testmode_fops`.

## Control flow
Initialization creates a directory named after the device under `usb_debug_root`, adds `params`, `hw_params`, `dr_mode`, optional gadget files, allocates a `debugfs_regset32`, and exposes `regdump`. Gadget state files read registers directly; endpoint files also take `hsotg->lock` while walking request queues. `testmode_write` copies a short command from userspace, maps known strings to USB test-mode constants, and calls `dwc2_hsotg_set_test_mode` under the spinlock. Exit removes the whole tree recursively and clears `debug_root`.

## State and persistence behavior
Debugfs entries are ephemeral runtime files. They expose live hardware and in-memory state but do not persist configuration. The only mutating interface is `testmode`, which can change controller test mode. The `regset` is devm-allocated and tied to the device lifetime, while debugfs dentries are manually removed.

## Dependencies and integration points
It depends on Linux debugfs, seq_file, uaccess, DWC2 core state/registers, USB test constants, gadget endpoint structures, and `usb_debug_root` from USB core. It integrates with `debug.h`, the DWC2 Makefile, and the platform probe/remove path.

## Risks
Reading registers through debugfs can trigger mode mismatch interrupts, acknowledged in the register table comment. Endpoint queue display must hold the lock to avoid list races, but register reads outside locks may still see transient state. `testmode_write` accepts prefix matches and maps unknown strings to `0`, so accidental writes can leave test mode rather than fail. Debugfs is not a stable ABI and must not be used as the only validation path.

## Test signals
With debugfs enabled, verify the DWC2 device directory, `params`, `hw_params`, `dr_mode`, `regdump`, and gadget files. Exercise reads during host and gadget operation, endpoint queue activity, and suspend/resume. Test test-mode writes for all supported names and unknown input. Watch dmesg for mode mismatch warnings, lockdep issues, and removal-time debugfs use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/debugfs.c -->
