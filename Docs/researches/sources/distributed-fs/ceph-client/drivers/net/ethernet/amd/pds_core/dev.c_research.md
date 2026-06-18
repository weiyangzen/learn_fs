# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/dev.c

## Purpose
`dev.c` implements low-level device-command interaction with AMD/Pensando firmware. It converts firmware status codes to Linux errors, checks firmware health, rings the device command doorbell, waits for command completion, resets/identifies the device, caches device identity strings and capabilities, and allocates/free MSI-X interrupt vectors based on firmware identity.

## Important APIs, Types, And Functions
Exported/internal APIs include `pdsc_err_to_errno`, `pdsc_is_fw_running`, `pdsc_is_fw_good`, `pdsc_devcmd_locked`, `pdsc_devcmd`, `pdsc_devcmd_init`, `pdsc_devcmd_reset`, `pdsc_dev_init`, and `pdsc_dev_uninit`. Helpers include `pdsc_devcmd_status`, `pdsc_devcmd_done`, `pdsc_devcmd_dbell`, `pdsc_devcmd_clean`, `pdsc_devcmd_str`, `pdsc_devcmd_wait`, `pdsc_devcmd_identify_locked`, `pdsc_init_devinfo`, and `pdsc_identify`.

## Control Flow
`pdsc_dev_init` begins by reading device info registers into `pdsc->dev_info` and firmware generation, sets the default device-command timeout, sends reset if firmware is running, identifies the device, publishes debugfs identity, allocates software interrupt metadata, and requests an exact number of MSI-X vectors capped by online CPUs and firmware `nintrs`.

Device commands are serialized by `devcmd_lock` unless a caller already holds it and uses `pdsc_devcmd_locked`. The locked function copies the command into MMIO command registers, clears `done`, rings the command doorbell, and calls `pdsc_devcmd_wait`. Waiting loops until firmware stops running, the done bit appears, or the timeout expires, sleeping briefly between polls. On timeout it cleans the command register area; on `-ENXIO` or timeout it queues health work when available; otherwise it copies the completion from MMIO.

Identify writes a Linux driver identity block into `cmd_regs->data`, runs `PDS_CORE_CMD_IDENTIFY`, copies firmware identity back from the same data window, and logs the firmware version if printable. Uninit frees all allocated interrupts through `pdsc_intr_free` and releases PCI IRQ vectors.

## State And Persistence
The file maintains runtime caches in `pdsc`: `fw_status`, `last_fw_time`, `last_hb`, `fw_generation`, `dev_info`, `dev_ident`, `devcmd_timeout`, `intr_info`, and `nintrs`. Device command data and completion are exchanged through MMIO BAR register windows. There is no filesystem persistence.

## Dependencies And Integration Points
It depends on PCI IRQ vector APIs, MMIO accessors, `utsname()` for driver identity, firmware ABI structures from `pds_core_if.h`, health work from `core.c`, debugfs identity publication, and interrupt free helpers. Higher layers in `core.c`, `devlink.c`, and `fw.c` use the device-command functions.

## Risks
The command data window is shared between identify, firmware update chunks, firmware list queries, and core init, so callers must hold `devcmd_lock` when touching `cmd_regs->data`. Firmware health checks update cached status as a side effect. Timeouts clean only command MMIO state and rely on health recovery for broader repair. Interrupt allocation requires exactly `nintrs` MSI-X vectors; partial availability is treated as failure. Error-code translation collapses several firmware statuses to generic Linux errors, which may hide detail from callers.

## Test Signals
Validation should cover identify success/failure, firmware stopped before command, timeout, bad PCI status, reset when firmware is already down, exact MSI-X allocation failure, printable and invalid firmware strings, debugfs identity creation, and health work queued after command transport failure.
