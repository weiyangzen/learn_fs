# sources/distributed-fs/ceph-client/drivers/watchdog/ibmasr.c

## Purpose
`ibmasr.c` implements the IBM Automatic Server Restart watchdog for several IBM xSeries machine families. It is a legacy `/dev/watchdog` miscdevice with fixed hardware timeout and model-specific I/O register layouts.

## Important APIs, types, and functions
Model selection uses `ibmasr_id_table` and DMI device descriptions. Global hardware parameters include ASR type, base/length, read/write addresses, toggle mask, and disable mask. Important helpers are `asr_get_base_address`, `asr_enable`, `asr_disable`, `asr_toggle`, and `__asr_toggle`. File operations implement write, ioctl, open, and release.

## Control Flow
Module init scans DMI for supported ASR descriptions, computes model-specific I/O addresses, reserves the region, and registers `/dev/watchdog`. Open toggles and enables the timer. Writes scan for magic close and toggle the hardware line. Ioctls support keepalive, enable/disable, support info, and fixed `GETTIMEOUT` of 256 seconds. Release disables only after magic close; otherwise it toggles and leaves the watchdog active.

## State and Persistence
All driver state is global. Hardware has a fixed timeout and persists until disabled. Module exit disables only when nowayout is false, then deregisters and releases I/O resources.

## Dependencies and Integration Points
The driver depends on DMI, raw I/O port access, legacy PCI config access for Jasper base discovery, miscdevice watchdog ABI, and module nowayout.

## Risks and Test Signals
Risks include DMI string fragility, unsafe Jasper PCI config probing, model-specific mask/address mistakes, fixed timeout expectations, and nowayout unload behavior. Tests should cover each ASR type, I/O region conflicts, magic close, unexpected close, enable/disable ioctl, fixed timeout return, and DMI no-match path.
