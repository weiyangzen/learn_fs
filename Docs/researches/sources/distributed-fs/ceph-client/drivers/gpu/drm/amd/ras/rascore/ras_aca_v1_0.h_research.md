# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca_v1_0.h

## Purpose

`ras_aca_v1_0.h` defines ACA v1.0 register bitfield extractors, status/IPID/MISC/SYND access macros, known external error codes, SMN MCA base constants, and the exported v1.0 ACA IP function table.

## Important APIs, Types, And Functions

Macros extract status validity, overflow, UC/CE/UE/deferred/poison/scrub, address LSB, error code/ext code, IPID MCA type/hardware ID/instance IDs, MISC0 valid/overflow/error count, and syndrome error information. It declares `extern const struct ras_aca_ip_func ras_aca_func_v1_0`.

## Control Flow, State, And Persistence

The header has no runtime flow. Its macros define how persistent hardware MCA register snapshots are decoded by `ras_aca_v1_0.c`.

## Dependencies And Integration Points

It includes `ras.h` for types and bit helpers and is consumed by ACA v1.0 parser and generic ACA code. The SMN constants are used to identify SMU MCA instances for GFX, SDMA, and MMHUB matching.

## Risks And Test Signals

Risks include wrong bit ranges, generation-specific constants being reused on incompatible hardware, and count/status macros not matching firmware documentation. Test signals include register decode unit tests, generated-register diffs, and validation against injected ACA bank dumps.
