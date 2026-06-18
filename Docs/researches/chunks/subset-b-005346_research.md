# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_os.c lines 8899-9958

## Scope And Purpose

This chunk is the tail of the QLogic qla4xxx iSCSI HBA OS-facing driver. It covers adapter removal, firmware DDB/session teardown, DMA addressing setup, SCSI device initialization, SCSI error-handler callbacks, host/application reset handling, PCI AER recovery, PCI device matching, and module registration.

The code bridges several kernel subsystems:

- PCI probe/remove and AER error recovery for supported QLogic iSCSI adapters.
- SCSI midlayer command abort, LUN reset, target reset, host reset, queue depth, and host reset ioctl callbacks.
- libiscsi transport registration and flash-node/session cleanup.
- qla4xxx firmware mailbox, DDB, ACB, IDC, interrupt, and adapter recovery helpers.

## Important APIs, Types, And Functions

- `qla4xxx_prevent_other_port_reinit()` finds the peer ISP4xxx PCI function in the same slot and sets `AF_HA_REMOVAL` on its `struct scsi_qla_host` so that peer port does not reinitialize while one port is being removed.
- `qla4xxx_destroy_ddb()` logs out one firmware DDB entry, polls firmware DDB state until no active connection or session failure, then clears the firmware DDB entry.
- `qla4xxx_destroy_fw_ddb_session()` walks all firmware DDB slots, tears down driver and libiscsi state for `FLASH_DDB` entries, and compensates the earlier `module_put()` used when flash sessions were created.
- `qla4xxx_remove_adapter()` is the PCI `.remove` callback. It destroys ifaces, boot sysfs state, flash DDB sessions, 8xxx sysfs attributes, DDB sysfs exports, the SCSI host, adapter resources, the SCSI host reference, and finally disables the PCI device.
- `qla4xxx_config_dma_addressing()` attempts a coherent 64-bit DMA mask and falls back to 32-bit DMA.
- `qla4xxx_sdev_init()` attaches the target `ddb_entry` to `sdev->hostdata` and sets the per-device queue depth from `ql4xmaxqdepth` or `QL4_DEF_QDEPTH`.
- `qla4xxx_del_from_active_array()` maps a firmware/driver request index back through SCSI tags, returns the command's `struct srb`, and adjusts adapter IOCB accounting for DMA-valid SRBs.
- `qla4xxx_eh_wait_on_command()` waits for a command's private `srb` pointer to become `NULL`, except during PCI channel/AER error handling.
- `qla4xxx_eh_wait_for_commands()` scans all SCSI tags for commands matching a target or specific device and waits for each matching command to drain.
- `qla4xxx_eh_abort()` implements SCSI abort handling with register-health checking, SRB reference pinning, `qla4xxx_abort_task()`, and optional completion wait.
- `qla4xxx_eh_device_reset()` performs iSCSI/SCSI LUN reset recovery: block SCSI EH through libiscsi, send firmware LUN reset, wait for commands for that LUN, then send a marker IOCB.
- `qla4xxx_eh_target_reset()` performs target-wide reset recovery: block SCSI EH, send firmware target reset, wait for all target commands, then send a warm target reset marker.
- `qla4xxx_eh_host_reset()` is the SCSI EH host reset path. It respects `ql4xdontresethba` and 83xx/84xx IDC DONTRESET coordination, waits for the HBA online, sets reset DPC bits, and calls `qla4xxx_recover_adapter()`.
- `qla4xxx_context_reset()` performs a firmware-context reset for non-80xx firmware reset requests by saving the primary ACB, disabling it, waiting for disable completion, and restoring it with `qla4xxx_set_acb()`.
- `qla4xxx_host_reset()` is the transport/application host reset hook in `qla4xxx_driver_template.host_reset`, accepting `SCSI_ADAPTER_RESET` or `SCSI_FIRMWARE_RESET`.
- `qla4xxx_pci_error_detected()`, `qla4xxx_pci_mmio_enabled()`, `qla4xxx_pci_slot_reset()`, and `qla4xxx_pci_resume()` implement the driver's `struct pci_error_handlers`.
- `qla4_8xxx_error_recovery()` coordinates ISP8022/8032/8042 AER slot reset recovery, chooses the reset owner among PCI functions, updates IDC/device state registers, reinitializes firmware, and re-enables interrupts.
- `qla4xxx_pci_tbl`, `qla4xxx_pci_driver`, `qla4xxx_module_init()`, and `qla4xxx_module_exit()` define device IDs, register the PCI driver, register/unregister the iSCSI transport, and manage the global SRB slab cache.

Key types and fields:

- `struct scsi_qla_host`: adapter-private state with `pdev`, `host`, `flags`, `dpc_flags`, `hardware_lock`, `iocb_cnt`, `boot_kset`, `task_wq`, firmware info, and `isp_ops`.
- `struct ddb_entry`: firmware device database/session object with `fw_ddb_index`, `ddb_type`, libiscsi `sess`/`conn`, and firmware DDB state.
- `struct srb`: per-SCSI-command request block with DMA validity, IOCB count, `cmd`, and `srb_ref` kref.
- `struct qla4xxx_cmd_priv`: per-`scsi_cmnd` private data containing the current `srb` pointer.
- Important flags include `AF_HA_REMOVAL`, `AF_ONLINE`, `AF_LINK_UP`, `AF_FW_RECOVERY`, `AF_EEH_BUSY`, `AF_PCI_CHANNEL_IO_PERM_FAILURE`, `DPC_RESET_HA`, `DPC_RESET_HA_FW_CONTEXT`, and `DPC_RESET_ACTIVE`.
- Timeout constants used in this chunk include `LOGOUT_TOV` for DDB logout polling, `EH_WAIT_CMD_TOV` for EH command completion waits, `HBA_ONLINE_TOV` for online waits, and `DISABLE_ACB_TOV` for ACB disable completion.

## Teardown And Removal Control Flow

`qla4xxx_remove_adapter()` first exits early when `pci_is_enabled(pdev)` is false. That case represents a failed probe path where resources were already unwound before the PCI core called remove. For live devices it retrieves `ha` from PCI driver data.

On ISP4xxx hardware, removal calls `qla4xxx_prevent_other_port_reinit()`. The peer function is computed from the current PCI function number: ISP4xxx iSCSI functions are 1 and 3, so function 1 selects peer function 3 and function 3 selects peer function 1. If the peer PCI device exists and has a nonzero `enable_cnt`, driver data is read and `AF_HA_REMOVAL` is set on the peer adapter. The peer device reference from `pci_get_domain_bus_and_slot()` is released with `pci_dev_put()`.

Removal then destroys user-visible and transport state in dependency order:

1. `qla4xxx_destroy_ifaces()` removes network/iSCSI iface sysfs objects.
2. `iscsi_boot_destroy_kset()` removes iSCSI boot sysfs state when boot sysfs is enabled and `ha->boot_kset` exists.
3. `qla4xxx_destroy_fw_ddb_session()` tears down firmware-backed flash DDB sessions.
4. `qla4_8xxx_free_sysfs_attr()` removes 8xxx-specific sysfs files.
5. `qla4xxx_sysfs_ddb_remove()` removes flashnode/sysfs DDB objects.
6. `scsi_remove_host()` detaches the SCSI host from the midlayer.
7. `qla4xxx_free_adapter()` releases adapter resources.
8. `scsi_host_put()` drops the host reference, and `pci_disable_device()` disables the PCI function.

`qla4xxx_destroy_fw_ddb_session()` walks `MAX_DDB_ENTRIES` and only acts on entries found by `qla4xxx_lookup_ddb_by_fw_index()` with `ddb_type == FLASH_DDB`. Each entry is logged out and cleared through `qla4xxx_destroy_ddb()`, then the libiscsi endpoint is destroyed, the DDB object is freed, and the session is torn down. The `try_module_get(qla4xxx_iscsi_transport.owner)` before `iscsi_destroy_endpoint()` balances earlier setup logic that deliberately dropped the module refcount for seamless driver unload with persistent flash sessions.

`qla4xxx_destroy_ddb()` first asks firmware to close the iSCSI session with `LOGOUT_OPTION_CLOSE_SESSION`. If logout fails, or if the DMA buffer allocation for reading the firmware DDB fails, it still clears the firmware DDB entry. On a successful logout and DMA allocation, it polls `qla4xxx_get_fwddb_entry()` once per second until firmware reports `DDB_DS_NO_CONNECTION_ACTIVE` or `DDB_DS_SESSION_FAILED`, a mailbox error occurs, or `LOGOUT_TOV` expires. The coherent DMA buffer is always released before the final `qla4xxx_clear_ddb_entry()` path.

## SCSI Device And Active Command Control Flow

`qla4xxx_sdev_init()` is invoked by the SCSI midlayer via the driver's `sdev_init` hook. It obtains the libiscsi class session from the SCSI target, retrieves the private `struct iscsi_session`, then obtains the `ddb_entry` from `sess->dd_data`. That `ddb_entry` is stored in `sdev->hostdata`, which is later used directly by LUN and target reset paths. Queue depth defaults to `QL4_DEF_QDEPTH` and can be overridden by the `ql4xmaxqdepth` module parameter when the value is nonzero and fits in 16 bits.

`qla4xxx_del_from_active_array()` no longer directly removes from a private array in this source shape; it uses `scsi_host_find_tag(ha->host, index)` to locate the command by tag, then reads `qla4xxx_cmd_priv(cmd)->srb`. For DMA-valid SRBs it subtracts `srb->iocb_cnt` from `ha->iocb_cnt` and poisons `cmd->host_scribble` with `MAX_SRBS` when the SRB still has a command pointer. This helper is externally declared in `ql4_glbl.h`, so completion and abort paths outside this chunk depend on its accounting behavior.

`qla4xxx_eh_wait_on_command()` polls the command-private `srb` pointer every two seconds for up to `EH_WAIT_CMD_TOV` iterations. It returns nonzero when the command has returned to the OS. During PCI channel offline or `AF_EEH_BUSY`, it returns `SUCCESS` immediately instead of waiting because PCI AER recovery is responsible for returning or aborting outstanding I/O.

`qla4xxx_eh_wait_for_commands()` scans tags from 0 to `ha->host->can_queue - 1`, finds commands with `scsi_host_find_tag()`, filters them by `scsi_target(cmd->device)` and optionally exact `sdev`, and calls `qla4xxx_eh_wait_on_command()` for each match. It returns 0 when all matching commands drained and 1 after the first command that fails to drain.

## SCSI Error Handler Reset Control Flow

`qla4xxx_eh_abort()` is the SCSI abort callback registered in `qla4xxx_driver_template.eh_abort_handler`. It logs the command, validates register access with `qla4xxx_isp_check_reg()`, then takes `ha->hardware_lock` to fetch the command's current SRB. If the SRB is already gone, the command completed and the abort succeeds. Otherwise the handler increments `srb_ref`, releases the lock, issues `qla4xxx_abort_task()`, drops the reference with `qla4xxx_srb_compl`, and waits for command completion only when firmware accepted the abort task. A mailbox failure or wait timeout causes `FAILED`.

`qla4xxx_eh_device_reset()` requires `cmd->device->hostdata` to hold a valid `ddb_entry`. It calls `iscsi_block_scsi_eh()` before doing firmware reset work so libiscsi can serialize EH against session state. The path checks registers, sends `qla4xxx_reset_lun(ha, ddb_entry, lun)`, waits for outstanding commands for only that SCSI device, and then sends `qla4xxx_send_marker_iocb(..., MM_LUN_RESET)`. The reset is reported successful only after all three firmware/midlayer steps succeed.

`qla4xxx_eh_target_reset()` is similar but target scoped. It uses the same libiscsi blocking and register check, sends `qla4xxx_reset_target()`, waits for all commands on the SCSI target regardless of LUN, then sends a marker with `MM_TGT_WARM_RESET`. It uses `starget_printk()` for target-scoped status messages.

`qla4xxx_eh_host_reset()` handles fatal SCSI EH recovery. It first checks register accessibility. On ISP8032/ISP8042 with `ql4xdontresethba`, it records the no-reset policy through `qla4_83xx_set_idc_dontreset()`. If the local module parameter or IDC state says not to reset the HBA, the handler optionally aborts all active commands with `DID_ABORT` when invoked from SCSI recovery and returns `FAILED`. Otherwise it waits for the adapter to be online, sets either `DPC_RESET_HA_FW_CONTEXT` for qla80xx devices or `DPC_RESET_HA` for older devices, calls `qla4xxx_recover_adapter()`, and reports `SUCCESS` only if recovery succeeds.

`qla4xxx_is_eh_active()` is a small helper that distinguishes SCSI EH recovery from application-triggered reset by testing `shost->shost_state == SHOST_RECOVERY`. That distinction matters in the "do not reset" branch, where active commands are force-aborted only in true EH context.

## Application And Firmware Context Reset Control Flow

`qla4xxx_host_reset()` is wired as `qla4xxx_driver_template.host_reset`, which is the SCSI host reset hook used by application paths such as sg reset rather than the SCSI EH host reset callback. It returns Linux negative errno values rather than SCSI `SUCCESS`/`FAILED`.

For `SCSI_ADAPTER_RESET`, it sets `DPC_RESET_HA`. For `SCSI_FIRMWARE_RESET`, it sets `DPC_RESET_HA_FW_CONTEXT` on qla80xx adapters, but on non-qla80xx adapters it performs `qla4xxx_context_reset()` directly and returns without a full adapter recovery. If `DPC_RESET_HA` is already set, it skips reset-type handling and goes straight to `qla4xxx_recover_adapter()`.

On ISP8032/ISP8042, an application-issued adapter reset also sets `GRACEFUL_RESET_BIT1` in `QLA83XX_IDC_DRV_CTRL` before recovery. This is an inter-driver coordination signal in IDC space, separate from the SCSI EH `DONTRESET` handling.

`qla4xxx_context_reset()` is an ACB-preserving firmware context reset. It allocates a coherent `struct addr_ctrl_blk_def`, zeroes it, reads the primary ACB with `qla4xxx_get_acb()`, disables the ACB with `qla4xxx_disable_acb()`, waits up to `DISABLE_ACB_TOV` for `ha->disable_acb_comp`, then restores the ACB with `qla4xxx_set_acb()`. Any mailbox failure is converted to `-EIO`, allocation failure to `-ENOMEM`, and the coherent buffer is freed on all post-allocation exits.

## PCI AER Recovery Control Flow

The chunk registers `qla4xxx_err_handler` in `qla4xxx_pci_driver.err_handler`. All callbacks first check `is_aer_supported(ha)` and return `PCI_ERS_RESULT_NONE` when the hardware/driver does not support this recovery model.

`qla4xxx_pci_error_detected()` handles the PCI core's channel-state notification:

- `pci_channel_io_normal`: clears `AF_EEH_BUSY` and returns `PCI_ERS_RESULT_CAN_RECOVER`.
- `pci_channel_io_frozen`: sets `AF_EEH_BUSY`, prematurely completes pending mailbox commands, frees IRQs, disables the PCI device, aborts all active commands with `DID_RESET`, and returns `PCI_ERS_RESULT_NEED_RESET`.
- `pci_channel_io_perm_failure`: sets both `AF_EEH_BUSY` and `AF_PCI_CHANNEL_IO_PERM_FAILURE`, aborts active commands with `DID_NO_CONNECT`, and returns `PCI_ERS_RESULT_DISCONNECT`.

`qla4xxx_pci_mmio_enabled()` is the callback after a `CAN_RECOVER` path where MMIO access works again. This implementation does not probe firmware health; it simply returns `PCI_ERS_RESULT_RECOVERED` when AER is supported.

`qla4xxx_pci_slot_reset()` restores PCI config state, re-enables the device, disables adapter interrupts through `ha->isp_ops`, and only attempts recovery for qla80xx adapters. Success from `qla4_8xxx_error_recovery()` maps to `PCI_ERS_RESULT_RECOVERED`; other paths leave the default `PCI_ERS_RESULT_DISCONNECT`.

`qla4xxx_pci_resume()` waits for the HBA to come online after slot or link reset and then clears `AF_EEH_BUSY` regardless of the wait result. A failed wait logs an error but does not change the PCI callback return because resume is a `void` hook.

`qla4_8xxx_error_recovery()` is the core 8xxx recovery routine. It sets `DPC_RESET_ACTIVE`, takes the adapter offline in software if `AF_ONLINE` was set, clears link state, fails all libiscsi sessions, and flushes DDB-change AEN processing. It then chooses a reset owner:

- ISP8022 scans lower PCI functions in the same slot. If any lower function is enabled, this function is not the reset owner.
- ISP8032/ISP8042 asks `qla4_83xx_can_perform_reset()`. If iSCSI can perform the reset, it forces `fn = 0` so the current function acts as owner.

The reset owner writes `QLA8XXX_DEV_COLD` under IDC lock, updates IDC registers, clears `AF_FW_RECOVERY`, and calls `qla4xxx_initialize_adapter(ha, RESET_ADAPTER)`. On failure it frees IRQs, clears driver-active state, and writes `QLA8XXX_DEV_FAILED`. On success it writes `QLA8XXX_DEV_READY`, clears `QLA8XXX_CRB_DRV_STATE`, sets driver-active state, unlocks IDC, and enables interrupts. Non-owner functions wait for `QLA8XXX_DEV_READY`, clear firmware-recovery state, reinitialize their adapter context, enable interrupts on success or free IRQs on failure, and set driver-active state. `DPC_RESET_ACTIVE` is cleared before return.

## Module Registration And Device Matching

`qla4xxx_pci_tbl` matches QLogic ISP4010, ISP4022, ISP4032, ISP8022, ISP8324, and ISP8042 PCI device IDs with wildcard subsystem IDs. `MODULE_DEVICE_TABLE(pci, qla4xxx_pci_tbl)` exports the table for module autoloading.

`qla4xxx_pci_driver` binds the device ID table to `qla4xxx_probe_adapter()`, `qla4xxx_remove_adapter()`, and the AER error handler table. Probe itself is earlier in `ql4_os.c`; this chunk provides its remove and error-recovery counterparts.

`qla4xxx_module_init()` optionally enables SCSI queue-full tracking when `ql4xqfulltracking` is set, creates the global `"qla4xxx_srbs"` slab cache for `struct srb`, derives `qla4xxx_version_str` from `QLA4XXX_DRIVER_VERSION` plus a `-debug` suffix when extended error logging is enabled, registers the libiscsi transport with `iscsi_register_transport()`, and finally registers the PCI driver. Failure unwinds in reverse order: unregister transport after PCI registration failure, destroy the SRB cache after transport registration failure, and return the error code.

`qla4xxx_module_exit()` unregisters the PCI driver first, then unregisters the iSCSI transport, then destroys the global SRB cache. The ordering ensures PCI devices are removed and adapter resources are torn down before transport operations and SRB allocations disappear.

## State And Persistence Behavior

State in this chunk is volatile kernel and firmware state rather than on-disk persistence.

- Peer-port removal coordination persists in `other_ha->flags` through `AF_HA_REMOVAL` until the peer adapter's state machine observes and clears or consumes it.
- Firmware DDB teardown mutates both firmware state (`qla4xxx_session_logout_ddb()`, `qla4xxx_clear_ddb_entry()`) and libiscsi/SCSI state (`iscsi_destroy_endpoint()`, `iscsi_session_teardown()`, `sdev->hostdata`).
- Command lifetime is represented by the per-command private `srb` pointer. EH wait loops treat `qla4xxx_cmd_priv(cmd)->srb == NULL` as command completion back to the OS.
- Adapter and link state are tracked in `ha->flags` (`AF_ONLINE`, `AF_LINK_UP`, `AF_FW_RECOVERY`, `AF_EEH_BUSY`, `AF_PCI_CHANNEL_IO_PERM_FAILURE`) and `ha->dpc_flags` (`DPC_RESET_HA`, `DPC_RESET_HA_FW_CONTEXT`, `DPC_RESET_ACTIVE`).
- Reset requests persist as DPC flags until `qla4xxx_recover_adapter()` and the DPC path consume and clear them. Application resets can also persist coordination bits in 83xx/84xx IDC registers.
- PCI AER frozen/permanent failure paths intentionally mark EEH busy and return outstanding commands with SCSI result codes before the slot reset or disconnect flow continues.
- Module-level state includes the global SRB slab cache, the registered iSCSI transport template, the registered PCI driver, and `qla4xxx_version_str`.

## Dependencies And Integration Points

- SCSI midlayer: `struct scsi_host_template`, `scsi_host_find_tag()`, `scsi_change_queue_depth()`, `scsi_remove_host()`, `scsi_host_put()`, SCSI EH return conventions, `SHOST_RECOVERY`, `struct scsi_device`, `struct scsi_target`, and host reset types.
- libiscsi and iscsi transport: `iscsi_register_transport()`, `iscsi_unregister_transport()`, `iscsi_block_scsi_eh()`, `iscsi_host_for_each_session()`, `iscsi_destroy_endpoint()`, `iscsi_session_teardown()`, `starget_to_session()`, and flashnode/sysfs operations registered in `qla4xxx_iscsi_transport`.
- PCI core and AER: `struct pci_driver`, `struct pci_error_handlers`, `pci_get_drvdata()`, `pci_is_enabled()`, `pci_disable_device()`, `pci_restore_state()`, `pci_enable_device()`, `pci_channel_offline()`, `pci_get_domain_bus_and_slot()`, and `pci_dev_put()`.
- DMA and memory allocation: `dma_set_mask_and_coherent()`, `dma_alloc_coherent()`, `dma_free_coherent()`, `kmem_cache_create()`, and `kmem_cache_destroy()`.
- qla4xxx mailbox/firmware helpers: `qla4xxx_session_logout_ddb()`, `qla4xxx_get_fwddb_entry()`, `qla4xxx_clear_ddb_entry()`, `qla4xxx_abort_task()`, `qla4xxx_reset_lun()`, `qla4xxx_reset_target()`, `qla4xxx_send_marker_iocb()`, `qla4xxx_get_acb()`, `qla4xxx_disable_acb()`, `qla4xxx_set_acb()`, `qla4xxx_recover_adapter()`, and `qla4xxx_initialize_adapter()`.
- qla4xxx 8xxx IDC and register helpers: `qla4_8xxx_rd_direct()`, `qla4_8xxx_wr_direct()`, `qla4_8xxx_update_idc_reg()`, `qla4_8xxx_set_drv_active()`, `qla4_8xxx_clear_drv_active()`, `qla4_83xx_can_perform_reset()`, `qla4_83xx_idc_dontreset()`, `qla4_83xx_set_idc_dontreset()`, `qla4_83xx_rd_reg()`, and `qla4_83xx_wr_reg()`.
- Driver internal lifecycle helpers: `qla4xxx_destroy_ifaces()`, `qla4xxx_sysfs_ddb_remove()`, `qla4xxx_free_adapter()`, `qla4xxx_free_irqs()`, `qla4xxx_fail_session()`, `qla4xxx_process_aen()`, and `qla4_8xxx_free_sysfs_attr()`.

## Risks And Edge Cases

- `qla4xxx_prevent_other_port_reinit()` checks `other_pdev->enable_cnt` and driver data without additional serialization against the peer's remove/probe path. Correctness depends on PCI device lifetime refs and the peer driver state being stable enough for this flag set.
- `qla4xxx_destroy_ddb()` clears the firmware DDB even when logout fails, the status poll fails, or the logout timeout expires. That favors teardown progress but can abandon an uncertain firmware/session state.
- `qla4xxx_destroy_fw_ddb_session()` assumes `ddb_entry->conn`, `ddb_entry->conn->ep`, and `ddb_entry->sess` are valid for every `FLASH_DDB` found in the lookup table.
- The module refcount compensation with `try_module_get()` before endpoint destruction is subtle. A mismatch with the earlier `module_put()` path would affect unload safety or leave an unexpected module reference.
- `qla4xxx_sdev_init()` assumes `starget_to_session()`, `cls_sess->dd_data`, and `sess->dd_data` are populated. A malformed target/session association would become a NULL dereference.
- `qla4xxx_del_from_active_array()` subtracts `srb->iocb_cnt` from `ha->iocb_cnt` without local underflow protection and only when `SRB_DMA_VALID` is set. Accounting correctness depends on one-time invocation for each active SRB.
- `qla4xxx_eh_wait_on_command()` can wait up to roughly 240 seconds because it sleeps two seconds for each `EH_WAIT_CMD_TOV` count. Long waits are normal for SCSI EH but can delay recovery escalation.
- The same wait helper returns `SUCCESS` immediately during AER/EEH. Callers interpret nonzero as "done", so AER paths must reliably return active commands through `qla4xxx_abort_active_cmds()`.
- `qla4xxx_eh_device_reset()` has a source comment noting a missing wait for HBA online before the LUN reset. If reset is issued while the adapter is not ready but register access still works, firmware reset commands can fail.
- Host reset and application reset use different return conventions (`SUCCESS`/`FAILED` versus negative errno), so callers must not mix the two APIs.
- `qla4xxx_context_reset()` ignores the return value from `wait_for_completion_timeout()`. It attempts to restore the ACB even if disable completion timed out.
- `qla4xxx_pci_mmio_enabled()` does not verify firmware health after MMIO is restored; it always reports recovered for AER-supported adapters.
- `qla4xxx_pci_slot_reset()` returns disconnect for non-qla80xx devices even after PCI config restore and device enable, because only qla80xx recovery is implemented in this path.
- `qla4xxx_pci_resume()` clears `AF_EEH_BUSY` even if `qla4xxx_wait_for_hba_online()` fails, which can let non-AER paths resume waiting or issuing work against an adapter that did not come online.
- In `qla4_8xxx_error_recovery()`, non-owner functions only reinitialize when `QLA8XXX_CRB_DEV_STATE` is already `QLA8XXX_DEV_READY`; there is no wait loop in this function for the owner to reach ready.
- `qla4xxx_module_init()` uses `strcpy()`/`strcat()` into `qla4xxx_version_str`; safety depends on that buffer being sized for `QLA4XXX_DRIVER_VERSION` plus `-debug`.

## Test Signals

Useful validation signals for this chunk include:

- PCI remove tests for failed-probe `!pci_is_enabled()` exit, normal remove ordering, ISP4xxx peer-port `AF_HA_REMOVAL` marking, boot kset removal enabled/disabled, and 8xxx sysfs cleanup.
- Flash DDB teardown tests covering logout success, logout mailbox failure, DMA allocation failure, DDB poll error, timeout, `DDB_DS_NO_CONNECTION_ACTIVE`, `DDB_DS_SESSION_FAILED`, and cleanup of endpoint/session/DDB objects.
- DMA mask tests where 64-bit coherent DMA succeeds and where it fails and falls back to 32-bit.
- SCSI device init tests for default queue depth, valid `ql4xmaxqdepth`, out-of-range `ql4xmaxqdepth`, and correct `sdev->hostdata` attachment.
- Active command accounting tests for missing tag, missing SRB, DMA-valid SRB accounting, host_scribble update, and repeated completion/abort races.
- SCSI EH tests for abort mailbox failure, abort success but command wait timeout, command already completed, register disconnect, LUN reset marker failure, target reset marker failure, and command-drain failures.
- Host reset tests for `ql4xdontresethba`, 83xx/84xx IDC DONTRESET, SCSI EH versus application reset behavior, HBA-online timeout, qla80xx firmware-context reset flagging, non-80xx ACB context reset, and recovery failure.
- PCI AER tests for normal, frozen, and permanent-failure channel states; mailbox premature completion; IRQ release; command abort result codes; slot reset `pci_enable_device()` failure; qla80xx owner and non-owner recovery; and resume clearing `AF_EEH_BUSY`.
- IDC/device-state tests verifying `QLA8XXX_DEV_COLD`, `QLA8XXX_DEV_READY`, `QLA8XXX_DEV_FAILED`, driver-active state, `QLA8XXX_CRB_DRV_STATE` clearing, and interrupt enable/disable ordering.
- Module load/unload tests for SRB slab allocation failure, iSCSI transport registration failure, PCI driver registration failure, debug version string suffix, queue-full tracking parameter, autoload device table coverage, and cleanup ordering on exit.
