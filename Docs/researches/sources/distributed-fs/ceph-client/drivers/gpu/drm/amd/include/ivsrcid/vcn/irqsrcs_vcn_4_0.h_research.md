# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_4_0.h

## Purpose
Defines VCN 4.0 source IDs for UVD trap/encode/system events, JPEG encode/decode engines, and poison events.

## Important APIs, Types, and Functions
No functions or types are declared. Key macros include UVD trap `114`, encoder general-purpose `119`, low-latency `120`, system-message `124`, JPEG encode `151`, JPEG decode `153`, JPEG1 decode `149`, JPEG2 decode aliased to JPEG encode `151`, JPEG3-7 decode `171`-`175`, and poison IDs `160`-`162`.

## Control Flow
No executable code is present. The constants guide interrupt dispatch to trap, encode, system-message, JPEG-engine, or poison handling.

## State and Persistence
The file has no state. The JPEG2 decode alias is a persistent compile-time mapping that consumers must handle carefully.

## Dependencies and Integration Points
The only local dependency is the include guard. Integration points include VCN 4.0 media interrupt registration, multi-JPEG decode routing, video fences, trap handling, and RAS poison paths.

## Risks and Test Signals
The standout risk is source ID overlap between JPEG2 decode and JPEG encode. Tests should validate all JPEG decode engines, encode completion, trap events, and poison reporting on VCN 4.0.
