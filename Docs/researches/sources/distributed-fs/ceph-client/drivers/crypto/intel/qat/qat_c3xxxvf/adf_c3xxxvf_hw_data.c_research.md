# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_c3xxxvf_hw_data.c

## Purpose
This file initializes hardware metadata for C3xxx virtual functions. A VF exposes one accelerator, one AE, one ETR bank, fixed TX/RX ring layout, VF interrupt callbacks, no local admin/arbiter/error-correction work, and PF/VF messaging for init/shutdown notification.

## Important APIs, Types, And Functions
Public functions are `adf_init_hw_data_c3xxxiov()` and `adf_clean_hw_data_c3xxxiov()`. Local helpers return fixed masks and BAR IDs (`get_accel_mask()`, `get_ae_mask()`, `get_num_accels()`, `get_num_aes()`, `get_misc_bar_id()`, `get_etr_bar_id()`, `get_sku()`), plus noop callbacks for unsupported PF-only operations.

## Control Flow
Initialization sets VF class data, bank/ring counts, fixed masks, Gen2 service map, VF ISR allocation/free callbacks, noop admin/arbiter/error-correction callbacks, `send_admin_init = adf_vf2pf_notify_init`, `disable_iov = adf_vf2pf_notify_shutdown`, Gen2 config, class index update, Gen2 VF PFVF ops, CSR ops, and DC ops. Cleanup decrements class instances and updates class indexes.

## State And Persistence Behavior
State is runtime-only in `hw_data` and the static VF class instance count. The VF relies on PF-mediated state through PF/VF messages rather than local firmware/admin ownership.

## Dependencies And Integration Points
It depends on Gen2 config/hw CSR/DC helpers, VF interrupt allocation, and PF/VF messaging helpers. The PCI VF driver calls these callbacks during probe/remove.

## Risks
Noop admin and arbiter callbacks mean common code must not assume PF-only resources on a VF. Fixed one-bank geometry must match hardware virtualization. Class index updates rely on device-manager ordering.

## Test Signals
VF probe should initialize one AE/one accelerator, exchange init/shutdown PF/VF messages, allocate VF interrupts, register crypto/compression instances appropriate to VF services, and clean up class indexes after VF removal.
