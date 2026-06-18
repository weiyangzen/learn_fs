# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/agilent_82357a.h

## Purpose
`agilent_82357a.h` defines the USB protocol constants, firmware registers, transfer flags, error codes, endpoint addresses, and private state for the 82357A/B USB GPIB driver.

## Important APIs, Types, and Functions
The header defines Agilent USB vendor/product IDs, pre-firmware IDs, endpoint addresses for A and B variants, bulk command opcodes, read/write/trailing flags, interrupt flag bit numbers, vendor error codes, control values for transfer abort/status, and firmware registers. `struct agilent_82357a_priv` stores USB interface, EOS settings, hardware control bits, interrupt flags, URBs, buffers, mutexes, timer, completion context, endpoints, and CIC/REN state. `struct agilent_82357a_register_pairlet` describes register transactions.

## Control Flow and State Model
The header itself has no runtime flow. It defines the protocol format consumed by `agilent_82357a.c`.

## Dependencies and Integration Points
It depends on USB, mutex, completion, timer, GPIB common, and TMS9914 headers. The definitions are private to the driver.

## Risks and Test Signals
The endpoint constants differ between 82357A and 82357B, so product selection must be exact. Transfer flag semantics drive END, ATN, abort, and count behavior. Tests should validate protocol packets against hardware traces or documentation and cover error-code translation.
