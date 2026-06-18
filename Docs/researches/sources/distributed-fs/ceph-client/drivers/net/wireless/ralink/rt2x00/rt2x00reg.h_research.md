# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00reg.h

## Purpose
`rt2x00reg.h` defines generic rt2x00 register-field infrastructure and cross-driver enum values for crypto status, antenna selection, LED modes, TSF synchronization, device power states, IFS/TXOP values, cipher IDs, rate modulation, and firmware validation errors. It is the low-level bitfield toolkit used by chip-specific register definitions and driver code.

## Important APIs, Types, And Functions
Core types are `struct rt2x00_field8`, `struct rt2x00_field16`, and `struct rt2x00_field32`, each storing a bit offset and mask. `FIELD8()`, `FIELD16()`, and `FIELD32()` validate constant masks at build time and compute offsets with compile-time first-set-bit macros. `rt2x00_set_field8/16/32()` and `rt2x00_get_field8/16/32()` write and extract values from register words with type checking. Enums define values used in descriptor and register programming, including `RX_CRYPTO_*`, `ANTENNA_*`, `LED_MODE_*`, `STATE_*`, `IFS_*`, `TXOP_*`, `CIPHER_*`, `RATE_MODE_*`, and `FW_*`.

## Control Flow
Chip register headers create field constants with `FIELD32(mask)` and driver code passes those constants to the set/get macros. This lets code modify named fields without manually shifting in every driver function. Busy-wait helpers in MMIO/USB also accept `struct rt2x00_field32` values to test hardware busy bits.

## State And Persistence
The header defines no runtime state beyond small field descriptors embedded in generated expressions. It standardizes values stored in hardware registers, firmware state, and descriptor summaries.

## Dependencies And Integration Points
It depends on kernel compile-time checks and `typecheck`. Nearly every rt2x00 source file that programs registers or descriptors depends on these enums and macros. `rt61pci.c` uses them extensively for CSR, BBP, RF, EEPROM, security, interrupt, and descriptor fields.

## Risks
The build-time field validation requires masks to be constant, non-zero, contiguous, and fit the target width. Incorrect masks fail compilation, which is useful but can surprise maintainers. `SET_FIELD` does not range-check the value before shifting, so oversized values are silently masked. The file also defines `is_power_of_two`, which can conflict conceptually with kernel helpers if included carelessly, although it is a macro local to this header usage.

## Test Signals
Test signals are successful compilation of all register definitions, sparse/typecheck coverage for wrong field widths, correct register programming in hardware traces, and no regressions in crypto, antenna, power-state, rate, or firmware error enum interpretation.
