# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbevf/ngbevf_type.h

## Purpose
`ngbevf_type.h` defines PCI device IDs and resource defaults for the Wangxun GbE VF driver.

## Important APIs, Types, and Functions
The header lists VF device IDs corresponding to WX1860 variants, and constants for one MSI-X vector, one RX/TX queue, 128 default TX/RX descriptors, and TX/RX work limits of 256.

## Control Flow
No executable control flow exists. The PCI ID table and VF software initialization consume these constants.

## State and Persistence Behavior
No state is stored. Constants become runtime limits in `struct wx` during probe.

## Dependencies and Integration Points
It is included by `ngbevf_main.c` and pairs with PF-supported VF device IDs.

## Risks and Edge Cases
Missing or incorrect device IDs prevent VF binding. Queue/vector limits must remain consistent with `ngbevf_set_num_queues()` and shared VF queue programming.

## Test Signals
Probe all listed VF IDs and validate queue/vector/ring defaults after `ngbevf_sw_init()`.
