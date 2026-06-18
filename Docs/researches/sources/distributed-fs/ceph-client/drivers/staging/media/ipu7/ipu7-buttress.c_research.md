# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress.c

## Purpose

This file controls the IPU7 buttress hardware block: secure CSE IPC, firmware authentication, IRQ demultiplexing, ISYS/PSYS power and clock transitions, D2D/NDE setup, timestamp sync/readout, wakeups, and buttress initialization/restoration.

## Important APIs, Types, and Functions

Public APIs include `ipu_buttress_ipc_reset()`, `ipu_buttress_powerup()`, `ipu_buttress_powerdown()`, `ipu_buttress_get_secure_mode()`, `ipu_buttress_authenticate()`, `ipu_buttress_reset_authentication()`, `ipu_buttress_auth_done()`, frequency getters, TSC sync/read/convert helpers, `ipu_buttress_wakeup_is_uc()`, `ipu_buttress_wakeup_ps_uc()`, `ipu_buttress_isr()`, `ipu_buttress_isr_threaded()`, `ipu_buttress_init()`, `ipu_buttress_restore()`, and `ipu_buttress_exit()`.

## Control Flow

Initialization sets mutexes/completions, CSE IPC register offsets/NACK mask, secure mode, WDT cache/ref clock, PB/buttress setup, and retries CSE IPC reset. IRQ handling obtains runtime PM if active, clears PB and buttress IRQs, dispatches IS/PS IRQ bits to auxiliary driver callbacks, handles CSE send/receive completions, disables IRQ bits that need threaded handling, and re-enables them after threaded callbacks. Powerup/down choose IPU7 or IPU8 paths, manage D2D/NDE for ISYS, request/release clock ownership or PS PLL as needed, program workpoint ratios, and poll power status. Authentication sends BOOT_LOAD and AUTH_RUN IPC commands and polls security/bootloader status.

## State and Persistence Behavior

`struct ipu_buttress` stores power/auth/console/IPC mutexes, CSE IPC completions and register addresses, cached WDT value, PSYS frequency fields, force flags, and reference clock. Hardware state persists in buttress MMIO registers and is restored by `ipu_buttress_restore()`.

## Dependencies and Integration Points

The file depends on PCI/runtime PM, firmware DMA state, auxiliary bus children, buttress register definitions, CPU model matching, and exported symbols for ISYS/PSYS modules. Authentication uses `isp->cpd_fw` and `psys->fw_sgt`.

## Risks and Edge Cases

CSE IPC has multiple timeout/retry paths and secure-mode bypasses. IRQ handling must avoid touching powered-down hardware; it uses `pm_runtime_get_if_active()`. Power transitions are generation-specific and polling-based. Authentication assumes firmware source registers point at the CPD package. TSC sync differs across IPU7/IPU7.5/IPU8.

## Test Signals

Signals include secure and non-secure boot, CSE reset/auth success and timeout/NACK failures, ISYS/PSYS runtime PM cycling, IRQ demux to child drivers, PB error logging, TSC sync/read conversion, suspend/resume restore, and IPU7/IPU7.5/IPU8 hardware variants.
