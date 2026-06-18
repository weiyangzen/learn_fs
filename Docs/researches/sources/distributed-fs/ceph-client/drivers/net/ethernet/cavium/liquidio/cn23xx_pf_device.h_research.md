# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_device.h

## Purpose
This header declares CN23XX PF-specific LiquidIO state and exported setup/control APIs.

## Important APIs, Types, And Functions
`struct octeon_cn23xx_pf` stores PF interrupt summary/enable MMIO pointers, an interrupt mask, and a configuration pointer. `struct oct_vf_stats` defines the mailbox-returned VF counters. Function declarations cover PF setup, OQ tick conversion, SR-IOV configuration, firmware-loaded detection, VF MAC-change notification, and VF stats retrieval.

## Control Flow
The generic LiquidIO probe allocates the chip state and calls `setup_cn23xx_octeon_pf_device()`. After setup, generic code calls function pointers installed by the implementation and may call the declared helpers for SR-IOV and VF management.

## State And Persistence
The header defines in-memory state only. Interrupt pointers map BAR0 offsets, while `conf` references LiquidIO static/runtime configuration.

## Dependencies And Integration Points
It includes `cn23xx_pf_regs.h` and depends on `struct octeon_device`, `struct octeon_config`, and kernel integer types from the surrounding LiquidIO headers.

## Risks
The header exposes `struct oct_vf_stats` wire shape for mailbox transfer; producer and consumer must keep size within mailbox data capacity. Callers must ensure the PF chip state is initialized before using interrupt pointers or configuration.

## Test Signals
Compile PF and shared-core builds, validate `sizeof(struct oct_vf_stats)` fits mailbox payload, and exercise each declared exported symbol through PF initialization and SR-IOV operations.
