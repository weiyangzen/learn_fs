# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_common_drv.h

## Purpose
This header is the shared internal driver interface for QAT common code and device-specific modules. It defines version/status bits, event/reset enums, service-handler structure, lifecycle prototypes, device-manager APIs, firmware-engine APIs, AER/reset APIs, transport/crypto/compression interfaces, ISR hooks, SR-IOV stubs or declarations, workqueue helpers, HAL/UOF loader APIs, and BAR accessor inlines.

## Important APIs, Types, And Functions
Key definitions include `ADF_DRV_VERSION`, status bits such as `ADF_STATUS_STARTED`, `enum adf_dev_reset_mode`, `enum adf_event`, and `struct service_hndl`. Important APIs include `adf_dev_up/down/restart()`, `adf_service_register/unregister()`, device-manager functions, reset/AER functions, `adf_ae_*()` firmware helpers, `adf_init_etr_data()`, `qat_crypto_*()`, `qat_compression_*()`, ISR allocation, workqueue helpers, SR-IOV/PFVF helpers, HAL/UOF loader functions, and inline `adf_get_pmisc_base()`, `adf_get_etr_base()`, and `adf_get_aram_base()`.

## Control Flow
The header itself has only inline BAR accessors and stubbed SR-IOV functions when `CONFIG_PCI_IOV` is disabled. Runtime control is implemented across common source files and invoked by PF/VF PCI modules.

## State And Persistence Behavior
No state is stored here, but the status bit assignments define `accel_dev->status` semantics and service handler bitmaps track per-device init/start states in implementations.

## Dependencies And Integration Points
It includes list/PCI headers, `adf_accel_devices.h`, firmware loader handle, and HAL definitions. It is included broadly by every QAT module.

## Risks
This is a high-impact internal ABI. Status-bit ordering, function prototypes, and SR-IOV stubs affect multiple generations. BAR accessor inlines rely on hardware-data callback correctness.

## Test Signals
Full QAT build matrix, PF/VF probe/start/stop/restart, crypto/compression algorithms, transport operations, SR-IOV on/off builds, AER reset, and firmware load validate this header.
