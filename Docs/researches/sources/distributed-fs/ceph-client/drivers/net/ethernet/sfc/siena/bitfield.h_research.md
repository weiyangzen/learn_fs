# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/bitfield.h

## Purpose
Provides Siena/Falcon register, descriptor, and DMA/MCDI bitfield helpers for 32-, 64-, and 128-bit little-endian hardware quantities.

## Important APIs and types
Defines `efx_dword_t`, `efx_qword_t`, and `efx_oword_t`; field metadata helpers `EFX_LOW_BIT`, `EFX_WIDTH`, `EFX_HIGH_BIT`; mask helpers; extraction helpers such as `EFX_DWORD_FIELD`, `EFX_QWORD_FIELD`, `EFX_OWORD_FIELD`; population helpers `EFX_POPULATE_*`; zero/set helpers; and read-modify-write helpers `EFX_SET_*_FIELD`, `EFX_AND_*`, and `EFX_OR_OWORD`.

## Control flow
There is no runtime control flow. Macro expansion extracts or inserts bit ranges from little-endian elements, using 32-bit or 64-bit paths depending on `BITS_PER_LONG`. Numbered populate wrappers pad unused fields with `EFX_DUMMY_FIELD`.

## State and persistence behavior
Manipulates caller-owned in-memory register and descriptor images. No allocation, MMIO, or persistence occurs directly.

## Dependencies
Relies on Linux endian types/conversions and generated field constants named with `_LBN` and `_WIDTH`. Used broadly by NIC register, descriptor, MCDI, and debug code.

## Risks
Wrong field constants silently corrupt hardware messages. Side-effectful macro arguments are unsafe. Shift-width and endian mistakes can be architecture-specific, especially across 32-bit and 64-bit builds.

## Test signals
Sparse/endian checks, 32-bit and 64-bit build coverage, descriptor/register construction tests, and hardware TX/RX/event smoke tests.
