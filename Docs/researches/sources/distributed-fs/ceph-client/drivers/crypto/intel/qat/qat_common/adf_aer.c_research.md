# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_aer.c

## Purpose
This file implements QAT PCI Advanced Error Reporting and reset recovery support. It handles PCI error callbacks, secondary bus reset/FLR helpers, asynchronous and synchronous device restart scheduling, SR-IOV reenablement, PF-to-VF fatal/restarted notifications, and fatal-error workqueue handling.

## Important APIs, Types, And Functions
Public objects/APIs include `adf_err_handler`, `adf_reset_sbr()`, `adf_reset_flr()`, `adf_dev_restore()`, `adf_notify_fatal_error()`, `adf_init_aer()`, and `adf_exit_aer()`. Internal worker data types are `struct adf_reset_dev_data`, `struct adf_sriov_dev_data`, and `struct adf_fatal_error_data`.

## Control Flow
`adf_error_detected()` sets restarting state, disables arbitration, notifies services/VFs, clears bus mastering, and stops the device. `adf_slot_reset()` restores PCI state, restarts the device, reenables SR-IOV, notifies VFs/services, and clears restarting. `adf_dev_aer_schedule_reset()` queues reset work and optionally waits. The reset worker restarts the device, queues SR-IOV reenablement, sends PF2VF restarted notification, and completes. Fatal error work notifies services, disables arbitration when autoreset is enabled, notifies VFs, and schedules reset.

## State And Persistence Behavior
State is runtime-only in status bits, workqueue items, completions, and global reset/SR-IOV workqueues. It does not persist across module unload.

## Dependencies And Integration Points
It depends on Linux PCI error handlers, workqueues, completions, common device lifecycle, PF/VF messaging, SR-IOV helpers, arbitration callbacks, and service notification hooks.

## Risks
Reset races are central: the code guards with `ADF_STATUS_RESTARTING`, but in-flight users and VFs must quiesce correctly. Sync reset has a 10-second timeout. Fatal autoreset depends on `autoreset_on_error`. Workqueue allocation failure disables recovery.

## Test Signals
PCI AER injection, fatal error notification, FLR/SBR recovery, VF fatal/restarted messages, SR-IOV reenablement after PF reset, service restarting/restarted callbacks, and timeout handling are key signals.
