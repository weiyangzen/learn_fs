# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_bank_state.h

## Purpose
This header defines the in-memory snapshot structure for QAT transport bank state and declares save/restore helpers used by hardware-data callbacks.

## Important APIs, Types, And Functions
Important types are `struct adf_bank_state_ring` for per-ring head/tail/config/base values and `struct adf_bank_state` for bank-level status, interrupt, coalescing, exception, service arbiter, and per-ring arrays sized by `ADF_ETR_MAX_RINGS_PER_BANK`. Public APIs are `adf_bank_state_save()` and `adf_bank_state_restore()`.

## Control Flow
No executable flow exists. The layout determines what `adf_bank_state.c` saves/restores.

## State And Persistence Behavior
The structures hold volatile snapshots. They are not stable persistent data and should be used only while the relevant device/bank configuration remains unchanged.

## Dependencies And Integration Points
It includes Linux types and is referenced by `struct adf_hw_device_data` callback members in `adf_accel_devices.h`, plus Gen4/Gen6 hardware-data implementations.

## Risks
The array size assumes the maximum per-bank ring count. Adding CSR fields without updating save/restore can lose state across resets. Layout changes affect any migration or reset users.

## Test Signals
Compile coverage and runtime ring-pair reset or migration tests that preserve queue/interrupt state validate this header.
