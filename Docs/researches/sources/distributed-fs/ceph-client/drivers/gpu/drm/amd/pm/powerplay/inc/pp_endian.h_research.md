# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_endian.h

## Purpose

`pp_endian.h` centralizes endian conversion between host CPU representation and SMC firmware table representation. The SMC side is treated as big-endian for 16-bit and 32-bit fields.

## Important APIs, Types, And Functions

The exported macros are `PP_HOST_TO_SMC_UL`, `PP_SMC_TO_HOST_UL`, `PP_HOST_TO_SMC_US`, `PP_SMC_TO_HOST_US`, and in-place conversion helpers `CONVERT_FROM_HOST_TO_SMC_UL`, `CONVERT_FROM_SMC_TO_HOST_UL`, and `CONVERT_FROM_HOST_TO_SMC_US`. They wrap Linux `cpu_to_be32`, `be32_to_cpu`, `cpu_to_be16`, and `be16_to_cpu`.

## Control Flow And Data Flow

There is no control flow. Data moves through these macros before tables or scalar values are copied to SMC memory or after values are read back from SMC memory. The in-place helpers assign converted values back to the passed lvalue.

## State And Persistence Behavior

The header has no state. The persistent effect is the byte order of data stored in SMC tables, firmware mailboxes, or local host copies after conversion.

## Dependencies And Integration Points

It depends on Linux endian helper macros supplied by includers or kernel headers. It integrates with SMU table upload/download paths, PP table transformations, firmware interface structures, and code exchanging 16-bit or 32-bit fields with SMC firmware.

## Risks And Edge Cases

Double conversion silently corrupts values. Missing conversion may only fail on host/firmware endian combinations not covered by test hardware. The header has no 64-bit helper, so multiword fields need explicit high/low handling. Callers should avoid lvalue expressions with side effects in in-place macros.

## Test Signals

Useful signals are table round-trip tests, SMC message/table upload on little-endian hosts, static review of conversion boundaries, and firmware version/clock/voltage values matching expected numeric ranges after readback.
