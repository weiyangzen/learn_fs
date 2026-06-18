# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_otpe2p.c

## Purpose
`mchp_pci1xxxx_otpe2p.c` implements the PCI1xxxx OTP/EEPROM auxiliary driver and registers NVMEM providers for byte-wise EEPROM and OTP access.

## Important APIs, Types, and Functions
Main state is `struct pci1xxxx_otp_eeprom_device`. Key helpers are `set_sys_lock()`, `release_sys_lock()`, `is_eeprom_responsive()`, EEPROM read/write callbacks, `otp_device_set_address()`, OTP read/write callbacks, `pci1xxxx_otp_eeprom_probe()`, and remove.

## Control Flow
Probe maps the PF3 system register window, acquires the system lock, powers OTP on, conditionally registers an EEPROM nvmem device if the EEPROM controller responds, releases the lock, then registers an OTP nvmem device. EEPROM operations lock PF3, clamp out-of-range count, perform one byte per busy-polled command, and release the lock. OTP operations set high/low address registers, issue read or byte-program commands, poll busy status, check pass/fail, and release the lock.

## State and Persistence
Driver state stores MMIO base and two `nvmem_config`/device pairs. Hardware persistence is the actual EEPROM/OTP contents; OTP writes are one-time programmable by device nature.

## Dependencies and Integration Points
Uses auxiliary bus metadata from the PCI parent, `devm_ioremap()`, `read_poll_timeout()`, and nvmem provider registration. With `NVMEM_SYSFS`, users can access exposed cells/files through sysfs.

## Risks
Byte-wise loops can be slow. OTP writes are irreversible and exposed through nvmem write callbacks. `set_sys_lock()` reads a 32-bit register into `u8`, which only validates low bits. Probe returns before releasing the sys lock if EEPROM nvmem registration fails after lock acquisition.

## Test Signals
Signals are successful OTP power-up/down, EEPROM responsiveness detection, bounded reads/writes at size edges, timeout/error behavior, sys lock release on errors, nvmem registration visibility, and safe behavior when EEPROM is absent.
