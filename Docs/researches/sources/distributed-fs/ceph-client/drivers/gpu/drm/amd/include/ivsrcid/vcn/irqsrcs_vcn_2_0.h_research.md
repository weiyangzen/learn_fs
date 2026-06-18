# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vcn/irqsrcs_vcn_2_0.h

## Purpose
Defines VCN 2.0 interrupt source IDs for video encode/system-message and JPEG encode/decode events, plus VCN 2.6 poison IDs.

## Important APIs, Types, and Functions
No functions or structs are present. VCN 2.0 macros include UVD encoder general-purpose `119`, low-latency `120`, system-message `124`, JPEG encode `151`, and JPEG decode `153`. VCN 2.6 poison macros are UVD `160`, DJPEG0 `161`, and EJPEG0 `162`.

## Control Flow
There is no executable flow. The macros let interrupt handlers branch to VCN encode, JPEG, firmware-message, or poison/error handling.

## State and Persistence
No runtime state exists. The constants are hardware source identifiers.

## Dependencies and Integration Points
The header depends only on its guard. Integration points include VCN 2.x ring interrupt setup, JPEG job completion, multimedia fences, and RAS poison handling.

## Risks and Test Signals
Risk includes using VCN 2.6 poison IDs without ASIC gating or swapping JPEG encode/decode IDs. Tests should cover VCN encode, JPEG encode/decode, system messages, and poison decode on supported hardware.
