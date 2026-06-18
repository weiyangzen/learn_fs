# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00usb.h

## Purpose
`rt2x00usb.h` declares the generic rt2x00 USB transport API, USB vendor request constants, register access wrappers, per-entry USB private structures, queue operations, lifecycle hooks, and USB driver entry points.

## Important APIs, Types, And Functions
Important constants include `REGISTER_TIMEOUT`, `REGISTER_TIMEOUT_FIRMWARE`, `EEPROM_TIMEOUT`, `CSR_CACHE_SIZE`, and vendor request type macros. `enum rt2x00usb_vendor_request` defines device-mode, single/multi register, EEPROM, LED, and RX control commands. `enum rt2x00usb_mode_offset` defines firmware/reset/sleep/wakeup/autoload mode offsets. Inline register helpers wrap buffered vendor requests for single and multi 32-bit reads/writes, including locked variants for callers already holding `csr_mutex`. Declared operations cover busy reads, async reads, radio disable, queue kicking/flushing/watchdog, entry clearing, initialization, uninitialization, probe/disconnect, and PM.

## Control Flow
USB chip drivers use this header to expose transport callbacks in their rt2x00lib ops. Register operations flow through vendor requests; large buffers are split through the CSR cache in `rt2x00usb.c`. Queue entries carry URBs, and beacon entries may use a larger private struct with a guardian URB when the chip requires a beacon guard byte. PM macros resolve suspend/resume to NULL when `CONFIG_PM` is disabled.

## State And Persistence
The header defines per-entry state only: `struct queue_entry_priv_usb` stores the main URB, while `struct queue_entry_priv_usb_bcn` extends it with guardian data and a guardian URB. Endpoint numbers and packet sizes are stored in `struct data_queue`, not in this header. No durable state is defined.

## Dependencies And Integration Points
It depends on Linux USB types and rt2x00 core structures. It is paired with `rt2x00usb.c` and used by USB chip drivers such as rt2500usb, rt73usb, and rt2800usb-style modules.

## Risks
The locked register helpers require `csr_mutex` to be held by convention enforced in the C file with `BUG_ON`. Buffer length must not exceed `CSR_CACHE_SIZE` for the locked cached path. The beacon private struct intentionally begins with the same layout as the generic USB private struct; changing field order would break casts in queue code. PM declarations differ by config, so users must use the provided macros.

## Test Signals
Signals include compilation of USB chip drivers, correct vendor request constants in bus traces, register access under locked and unlocked paths, beacon guardian URB allocation when required, PM builds with and without `CONFIG_PM`, and endpoint queue operations resolving through the declared API.
