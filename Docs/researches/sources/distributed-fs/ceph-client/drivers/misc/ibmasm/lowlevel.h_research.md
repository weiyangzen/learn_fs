# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/lowlevel.h

## Purpose
`lowlevel.h` defines Condor service-processor PCI IDs, mailbox registers, interrupt masks, UART base offsets, and inline MMIO helpers for IBM ASM low-level communication.

## Important APIs, Types, and Functions
Constants include IBM vendor/device IDs, inbound/outbound queue ports, interrupt status/control registers, SP/UART masks, Scout COM base offsets, `NO_MFAS_AVAILABLE`, and mailbox bit helpers. Inline functions cover interrupt pending checks, interrupt enable/disable, MFA inbound/outbound get/set, valid-MFA checks, and converting an MFA to an `i2o_message` pointer.

## Control Flow
Higher-level code uses these helpers to mask/unmask SP and UART interrupts, poll for outbound MFAs with a short retry loop, detect full inbound mailbox, and translate mailbox frame addresses into MMIO pointers.

## State and Persistence
No software state is stored; helpers directly read and write MMIO registers.

## Dependencies and Integration Points
It includes `asm/io.h` and is consumed by module setup, low-level transport, heartbeat, command paths, and UART registration.

## Risks and Edge Cases
MMIO helpers have no locking or memory barriers beyond accessor semantics. `get_mfa_outbound()` loops without delay. `get_i2o_message()` trusts the MFA address after masking and maps it into the device BAR window.

## Test Signals
Hardware or emulated tests should verify interrupt mask bit polarity, inbound full handling, outbound invalid retry behavior, MFA address masking, and UART/SP interrupt coexistence.
