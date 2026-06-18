# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_5_0.h

## Purpose
Defines VCN 5.0 interrupt source IDs for video trap/encode/system events, JPEG encode/decode engines, and poison events.

## Important APIs, Types, and Functions
There are no functions or structs. The macros include UVD trap `114`, encoder general-purpose `119`, low-latency `120`, system-message `124`, JPEG encode `151`, JPEG decode `153`, JPEG1 `149`, JPEG2 `151`, JPEG3-7 `171`-`175`, JPEG8 `177`, JPEG9 `178`, and poison IDs UVD `160`, DJPEG0 `161`, EJPEG0 `162`.

## Control Flow
The header has no executable flow. Interrupt handlers use these source IDs to select VCN 5.0 trap, encode, JPEG, firmware-message, or poison handling.

## State and Persistence
No runtime state is stored. The source IDs are stable event contracts.

## Dependencies and Integration Points
The include guard is the only dependency. Integration points include VCN 5.0 media block init, multi-JPEG ring interrupt handling, fence signaling, trap routing, and RAS poison reporting.

## Risks and Test Signals
Risks include JPEG2/JPEG encode overlap and missed coverage for added JPEG8/JPEG9 engines. Tests should run per-engine JPEG decode, encode queues, trap handling, and poison interrupt reporting.
