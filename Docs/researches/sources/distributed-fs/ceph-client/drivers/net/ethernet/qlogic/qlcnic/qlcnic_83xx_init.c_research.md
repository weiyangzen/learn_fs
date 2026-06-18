# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_init.c

## Purpose
This file implements 83xx-family adapter initialization, inter-driver communication (IDC) state handling, firmware reset/restart, reset-template execution, vNIC/default operating-mode selection, firmware-image loading, POST execution, and PCI AER recovery hooks. It is the main orchestration layer that brings a 83xx device from firmware/flash state into a running NIC function and keeps all PCI functions coordinated during reset and failure recovery.

## Important APIs, Types, And Functions
- Reset-template structures: `struct qlc_83xx_reset_hdr`, `struct qlc_83xx_entry_hdr`, `struct qlc_83xx_poll`, `struct qlc_83xx_rmw`, `struct qlc_83xx_entry`, and `struct qlc_83xx_quad_entry` describe the flash-provided command stream used to stop, initialize, and start hardware.
- IDC exported entry points: `qlcnic_83xx_idc_init()`, `qlcnic_83xx_idc_exit()`, `qlcnic_83xx_idc_poll_dev_state()`, `qlcnic_83xx_idc_request_reset()`, `qlcnic_83xx_idc_ready_state_entry()`, `qlcnic_83xx_idc_vnic_pf_entry()`, and `qlcnic_83xx_idc_reattach_driver()`.
- Main adapter init: `qlcnic_83xx_init()` initializes mailbox work, SR-IOV/VF paths, flash descriptors, IDC, interrupts, DCB, NIC mode, and mode-specific driver setup.
- Firmware/restart helpers: `qlcnic_83xx_restart_hw()`, `qlcnic_83xx_copy_bootloader()`, `qlcnic_83xx_copy_fw_file()`, `qlcnic_83xx_load_fw_image_from_host()`, and `qlcnic_83xx_run_post()`.
- Template executor: `qlcnic_83xx_exec_template_cmd()` dispatches opcodes such as write-list, read/write-list, poll-list, poll-write-list, read-modify-write, sequence pause/end, template end, and poll-read-list.
- Opmode and rings: `qlcnic_83xx_get_nic_configuration()`, `qlcnic_83xx_configure_opmode()`, `qlcnic_83xx_init_default_driver()`, `qlcnic_83xx_config_buff_descriptors()`, and `qlcnic_83xx_init_rings()`.
- AER hooks: `qlcnic_83xx_aer_stop_poll_work()`, `qlcnic_83xx_aer_reset()`, and `qlcnic_83xx_aer_start_poll_work()`.

## Control Flow
`qlcnic_83xx_init()` sets MSI-X preference, POST mode from `qlcnic_load_fw_file`, initializes default ring counts, creates mailbox work, and diverts SR-IOV VFs into `qlcnic_sriov_vf_init()`. For PF/default paths it reads flash metadata, verifies command PEG/heartbeat, allocates firmware metadata, initializes IDC, sets up interrupts/mailbox interrupts, clears stale function resources, enables DCB, initializes the NIC, chooses default/vNIC mode, calls `adapter->nic_ops->init_driver`, and starts periodic IDC polling.

IDC state is driven by `qlcnic_83xx_idc_poll_dev_state()`, which reads `QLC_83XX_IDC_DEV_STATE`, validates legal transitions, dispatches to handlers for READY, NEED_RESET, NEED_QUIESCENT, FAILED, INIT, and QUIESCENT, updates previous state, runs periodic filter pruning, and reschedules while `QLC_83XX_MODULE_LOADED` is set. READY checks temperature, firmware heartbeat, graceful reset requests, firmware dump requests, TX soft reset requests, and quiesce requests. NEED_RESET detaches the driver, disables mailbox readiness, optionally disables vNIC mode, waits for diagnostic completion, ACKs reset, waits for peer function ACKs, and transitions to INIT. INIT lets the reset owner restart hardware. FAILED records errors and may stop hardware/dump firmware if reset recovery is disabled.

Hardware restart is reset-template based. `qlcnic_83xx_get_reset_instruction_template()` reads a template header and body from flash, validates checksum, and records stop/start/init offsets. `qlcnic_83xx_restart_hw()` executes stop/init/start phases, optionally dumps firmware, copies bootloader to memory, optionally runs POST firmware, chooses host or flash firmware image, starts hardware, and validates command PEG plus heartbeat.

## State And Persistence Behavior
Persistent adapter state lives in `adapter`, `adapter->ahw`, hardware CRB/shared registers, firmware image-valid registers, and flash-provided reset templates. IDC uses hardware registers including driver presence, ACK, audit, major/minor version, control, and device-state registers so multiple PCI functions coordinate through device-visible state rather than process-local state. The reset template is cached in `ahw->reset.buff` and reused unless the firmware version increases. Work scheduling uses `adapter->fw_work` and `adapter->idc_aen_work`; module-loaded and resetting bits gate polling and concurrent reset operations. Firmware images are transiently requested from userspace firmware storage and released after copying.

## Dependencies And Integration Points
This file depends heavily on `qlcnic.h`, `qlcnic_hw.h`, `qlcnic_sriov.h`, mailbox helpers, flash access, indirect register access, firmware dump/minidump helpers, interrupt setup, DCB attach/info, SR-IOV PF/VF reinit/reset helpers, netdev open/close paths, and vNIC configuration implemented in `qlcnic_83xx_vnic.c`. It exports reset and init hooks consumed by the main qlcnic adapter probe/remove, watchdog, AER, and ethtool dump/reset request paths.

## Risks And Edge Cases
- IDC correctness depends on shared-register locking through `qlcnic_83xx_lock_driver()`; skipped or failed locking can strand peer functions in NEED_RESET/INIT states.
- Reset ACK timeout forcibly clears non-ACKing functions from presence, which allows recovery but can hide a stuck function.
- The reset-template interpreter trusts flash-provided sizes/offsets after checksum validation; malformed templates can drive unexpected register operations.
- `qlcnic_83xx_reset_template_checksum()` has inverted-looking success logic (`~sum` returns success), so checksum behavior deserves focused review against hardware format.
- Some quiesce paths are logged as `TBD`, making graceful quiesce less complete than reset handling.
- Firmware restart performs blocking sleeps, DMA/MS memory writes, and firmware requests in recovery paths; callers must be in sleepable context.
- AER reset relies on reset-owner election and `idc->state_entry`; incorrect opmode/state-entry assignment can leave devices detached.

## Test Signals
Useful validation signals include probe success through `qlcnic_83xx_init()`, IDC state transition logs, successful command PEG/heartbeat checks, firmware dump/reset requests through ethtool, POST pass/fail signatures, vNIC mode enable/disable state, DCB info refresh after reattach, AER reset recovery, and absence of stuck `__QLCNIC_RESETTING` or `QLC_83XX_MODULE_LOADED` states after remove.
