# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_ierb.c

## Purpose
Implements the LS1028A ENETC Integrated Endpoint Register Block platform driver. It fixes boot-time IERB FIFO/buffer parameters that are copied into ENETC PFs after FLR and are read-only from PF space.

## Important APIs, Types, and Functions
Exports `enetc_ierb_register_pf`. Internal components are `struct enetc_ierb`, `enetc_ierb_write`, `enetc_ierb_probe`, the OF match table for `fsl,ls1028a-enetc-ierb`, and the platform driver registration.

## Control Flow
Probe allocates driver state, maps the IERB resource, sets the free buffer depletion threshold, and stores drvdata. A PF later calls `enetc_ierb_register_pf`, which maps the PCI function to an ENETC port, defers if the platform driver is not ready, calculates TX byte credit, TX memory allocation, and RX credit from `ENETC_MAC_MAXFRM_SIZE`, then writes the per-port IERB registers.

## State and Persistence
Persistent state is IERB hardware configuration: transmit byte credit, transmit memory byte allocation, receive initial credits, and global free-memory depletion threshold. Software state only stores the mapped IERB base pointer. Values survive as platform register state and influence PF behavior after FLR.

## Dependencies and Integration Points
Depends on `enetc_pf_to_port`, ENETC max frame constants, platform device probing, and the PF probe path in `enetc_pf.c` that locates this device by compatible string. The header provides a no-op/stub path when the driver is disabled.

## Risks
Risks include PF probing before IERB readiness, stale device trees that omit the IERB node, port-number mapping errors, and hard-coded formulas that assume the jumbo/preemption memory recommendations remain valid. Misprogramming can cause FIFO depletion, frame drops, or RX lock-up under jumbo and preemption traffic.

## Test Signals
Probe ordering should handle `-EPROBE_DEFER`; PF probe should warn but continue on missing unavailable IERB. Validate register writes against LS1028A datasheet recommendations, jumbo frame traffic, frame preemption traffic, FLR behavior, and multi-port contention under high RX/TX load.
