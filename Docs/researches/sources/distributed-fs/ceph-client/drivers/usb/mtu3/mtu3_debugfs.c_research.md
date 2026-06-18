# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_debugfs.c

## Purpose

`mtu3_debugfs.c` creates MTU3 debugfs controls and diagnostics for register dumps, endpoint state, FIFO allocation, QMU rings/GPDs, probe registers, manual dual-role mode switching, and VBUS control.

## Important APIs, Types, and Functions

Register arrays `mtu3_ippc_regs`, `mtu3_dev_regs`, `mtu3_csr_regs`, and `mtu3_prb_regs` define debugfs regsets. Show functions include `mtu3_link_state_show()`, `mtu3_ep_used_show()`, `mtu3_ep_info_show()`, `mtu3_fifo_show()`, `mtu3_qmu_ring_show()`, and `mtu3_qmu_gpd_show()`. Public helpers are `ssusb_dev_debugfs_init()`, `ssusb_dr_debugfs_init()`, `ssusb_debugfs_create_root()`, and `ssusb_debugfs_remove_root()`.

## Control Flow

Platform probe creates the root directory named after the device. Gadget init adds register regsets, per-endpoint directories, QMU/FIFO views, probe-register read/write files, and link/endpoint summaries. In manual DRD mode, dual-role init adds `mode` and `vbus` writable files. Writes to `mode` queue role switches through `ssusb_mode_switch()`, and writes to `vbus` call `ssusb_set_vbus()`.

## State and Persistence Behavior

Debugfs reflects live hardware and driver state. Endpoint and QMU state reads take `mtu->lock`; probe writes directly modify selected IPPC probe registers. No settings persist after remove, though manual writes affect live role/VBUS state until changed.

## Dependencies and Integration Points

The file depends on debugfs, seq_file, user-copy helpers, regulator state, MTU3 register definitions, endpoint/QMU structures, and dual-role helpers. It is optional through `CONFIG_DEBUG_FS` and called from `mtu3_plat.c`, `mtu3_core.c`, and `mtu3_dr.c`.

## Risks and Test Signals

Risks include privileged users writing probe registers that can disturb hardware, direct VBUS toggles outside normal role policy, buffer parsing without explicit NUL termination after short copy windows, and debugfs file creation failures being intentionally nonfatal. Test signals include reading all regsets, endpoint directories appearing after gadget init, manual `mode` switches host/device, VBUS on/off writes, QMU GPD dumps while endpoints are enabled, and recursive cleanup on remove.
