# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_vnic.c

## Purpose
This file implements 83xx vNIC/NPAR operating-mode setup. It decides whether a PCI function is management, privileged, or non-privileged, configures function opmode registers, initializes the correct vNIC role, manages vNIC operational state, and records eSwitch enablement per physical port.

## Important APIs, Types, And Functions
- `qlcnic_83xx_config_vnic_opmode()` reads `QLC_83XX_DRV_OP_MODE`, derives function privilege, assigns `ahw->op_mode`, sets IDC state-entry callbacks, and assigns `adapter->nic_ops->init_driver`.
- `qlcnic_83xx_init_mgmt_vnic()` initializes the management function, reads PCI/NIC partition information, sets opmode, default offload settings, port info, descriptor limits, MSI-X support, and enables vNIC mode.
- `qlcnic_83xx_init_privileged_vnic()` and `qlcnic_83xx_init_non_privileged_vnic()` initialize privileged and VF-like non-privileged vNIC roles.
- `qlcnic_83xx_set_vnic_opmode()` marks the current function as management in the driver opmode register.
- `qlcnic_83xx_disable_vnic_mode()` and internal `qlcnic_83xx_enable_vnic_mode()` write `QLC_83XX_VNIC_STATE`.
- `qlcnic_83xx_check_vnic_state()` waits for management function to make vNIC mode operational.
- `qlcnic_83xx_set_port_eswitch_status()` queries NIC info and marks an eSwitch as enabled for a port.

## Control Flow
`qlcnic_83xx_configure_opmode()` in the init file calls `qlcnic_83xx_config_vnic_opmode()` when NIC capabilities indicate eSwitch/vNIC mode. This file first records the PCI function number, reads opmode, maps default opmode to management, and selects the role-specific init routine. Management functions perform partition discovery and opmode programming, reset NPAR config on reinit, fetch port info, configure descriptors, and write vNIC state operational. Privileged functions wait for management-enabled vNIC mode through `qlcnic_83xx_idc_vnic_pf_entry()` in the init file. Non-privileged functions refresh firmware version, apply eSwitch port config, get port info, and use vNIC descriptor limits.

## State And Persistence Behavior
The primary persistent state is hardware-backed: `QLC_83XX_DRV_OP_MODE` encodes per-function privilege, and `QLC_83XX_VNIC_STATE` indicates NPAR operational state. The adapter mirrors this in `ahw->op_mode`, `ahw->idc.vnic_state`, `ahw->idc.vnic_wait_limit`, flags such as `QLCNIC_ADAPTER_INITIALIZED` and `QLCNIC_ESWITCH_ENABLED`, descriptor counts, ring limits, MSI-X support, and MAC learning booleans.

## Dependencies And Integration Points
This file depends on IDC callbacks from `qlcnic_83xx_init.c`, PCI/NIC information helpers from context/mailbox code, port-info and default-offload helpers, eSwitch configuration routines, global `qlcnic_use_msi_x`, and adapter templates in `adapter->nic_ops`. It is the vNIC-specific branch of 83xx initialization and is also used during reset recovery when vNIC mode must be disabled or re-enabled.

## Risks And Edge Cases
- Management-function initialization is the only path that enables vNIC mode; privileged functions can time out if management does not finish.
- `qlcnic_83xx_set_vnic_opmode()` always programs the current function as management when called by management init, so misidentifying privilege can affect all functions.
- Non-privileged initialization assumes eSwitch port configuration succeeds before port info/ring setup.
- `qlcnic_83xx_check_vnic_state()` sleeps in one-second increments and consumes `vnic_wait_limit`; callers need to reset the wait limit before reuse.
- eSwitch enablement is based on firmware capabilities returned by `qlcnic_get_nic_info`; stale/failed mailbox responses disable the path.

## Test Signals
Test signals include logs identifying Management/Privileged/Virtual function HAL version, successful vNIC operational state transition, timeout logs from `qlcnic_83xx_check_vnic_state()`, descriptor counts appropriate to 1G/10G ports, `QLCNIC_ESWITCH_ENABLED` flag behavior, and correct RX MAC learning behavior when `drv_mac_learn` is enabled.
