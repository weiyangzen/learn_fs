# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/bitfield.h

Purpose: Provides Solarflare bitfield manipulation primitives for little-endian 32-bit, 64-bit, and 128-bit hardware words. The SFC drivers use it to build and inspect firmware, descriptor, register, and DMA data structures without relying on native 128-bit integer types.

Important APIs and types: Defines field metadata helpers (`EFX_LOW_BIT`, `EFX_WIDTH`, `EFX_HIGH_BIT`), mask helpers, little-endian wrapper unions `efx_dword_t`, `efx_qword_t`, and `efx_oword_t`, printk format/value macros, extraction macros for 32-bit and 64-bit host word strategies, zero/all-ones tests, populate macros for up to 19 field/value pairs, zero/set helpers, bitwise invert/and/or helpers, read-modify-write field setters, DMA width helper macros, and static initializer `EFX_OWORD32()`.

State and dependencies: The header has no runtime state but encodes an ABI-safe representation of NIC fields in little-endian memory. It depends on kernel endian types, `BITS_PER_LONG`, DMA address width, and the convention that each hardware field has `_LBN` and `_WIDTH` macros.

Risks and test signals: Macro arguments can be evaluated multiple times in some helpers, and widths outside supported ranges can cause invalid shifts if field metadata is wrong. Correctness varies by 32-bit versus 64-bit builds. Tests should compile and exercise extraction, populate, and set macros on both word sizes, fields spanning element boundaries, full-width 32/64 masks, zero/all-ones checks, DMA address width truncation, and representative SFC descriptor/register definitions.
