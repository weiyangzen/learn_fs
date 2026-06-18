# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_1_0.h

## Purpose
Defines VCN 1.0 interrupt source IDs for UVD-compatible encoder and system-message events.

## Important APIs, Types, and Functions
No functions or types exist. The macros are encoder general-purpose `119`, encoder low-latency `120`, and UVD system-message interrupt `124` in the `VCN_1_0__SRCID__*` namespace.

## Control Flow
No code executes here. The values route VCN 1.0 interrupts to encoder completion or firmware-message handling.

## State and Persistence
There is no mutable state. The constants are persistent hardware identifiers.

## Dependencies and Integration Points
The file depends only on its include guard. Integration points include VCN 1.0 ring setup, UVD-compatible interrupt decode paths, video fences, and firmware message handling.

## Risks and Test Signals
Legacy UVD naming inside a VCN header can cause confusion with later VCN JPEG events. Tests should validate VCN 1.0 encode and system-message interrupts with source IDs `119`, `120`, and `124`.
