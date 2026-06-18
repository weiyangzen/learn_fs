# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_vcap_impl.c

## Purpose
This file declares the LAN969x VCAP instance layout for the shared Sparx5 VCAP implementation. It maps logical VCAP types and chain ranges to physical blocks, map IDs, lookup counts, and ingress/egress direction.

## Important APIs, Types, And Functions
The exported object is `lan969x_vcap_inst_cfg[]`, an array of `struct sparx5_vcap_inst`. It defines three IS0 CLM instances, two IS2 instances, one ES0 instance, and one ES2 instance.

## Control Flow
There is no executable control flow beyond static initialization. Common Sparx5 VCAP initialization iterates this array to create `vcap_admin` blocks, determine chain ownership, program block numbers, and expose the correct VCAPs for tc rule insertion.

## State And Persistence
The array is static read-only configuration. It influences runtime VCAP admin state and hardware initialization but does not mutate state itself.

## Dependencies And Integration Points
It depends on common Sparx5 VCAP chain constants, lookup constants, `struct sparx5_vcap_inst`, and generated LAN969x VCAP metadata. The file is compiled only when LAN969x support is selected.

## Risks And Edge Cases
Chain boundaries must be contiguous and non-overlapping; otherwise tc chain routing can install rules in the wrong physical VCAP. IS0/IS2 `lookups_per_instance` uses integer division assumptions. ES0 and ES2 use count-based layouts rather than block numbers, so common code must handle both patterns. Incorrect `ingress` flags would route rule validation and default fields incorrectly.

## Test Signals
Test tc filters on every advertised chain range, verify debugfs VCAP instances, confirm IS0 CLM0/1/2 and IS2-0/1 rule placement, and validate ES0/ES2 egress rules after LAN969x probe.
