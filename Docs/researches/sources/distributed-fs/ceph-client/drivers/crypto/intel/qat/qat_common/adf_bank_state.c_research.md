# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_bank_state.c

## Purpose
This file saves and restores QAT transport bank/ring CSR state across bank reset or migration-related flows. It snapshots ring base/config/head/tail registers plus interrupt/status/coalescing/arbiter state and verifies selected status registers after restore.

## Important APIs, Types, And Functions
Public APIs are `adf_bank_state_save()` and `adf_bank_state_restore()`. Important helpers are `bank_state_save()`, `bank_state_restore()`, and `check_stat()`. The implementation uses `struct adf_hw_csr_ops` callbacks and `struct adf_bank_state` from the companion header.

## Control Flow
Save validates bank number, obtains ETR base and CSR ops, then reads bank-level status/interrupt/control registers and each ring's head/tail/config/base. Restore writes ring bases/configs, restores TX and RX head/tail with TX/RX gap handling, restores interrupt/coalescing/exception/arbiter registers, rewrites interrupt source selection with rise/fall masks, then verifies key status registers with `check_stat()`.

## State And Persistence Behavior
State is caller-owned in `struct adf_bank_state`; this file only fills/restores it. The saved state is volatile and valid only for matching device generation/bank geometry.

## Dependencies And Integration Points
It depends on `adf_accel_devices.h` CSR callback table, common BAR helpers, bank geometry in `hw_data`, and callers such as Gen4/Gen6 hardware-data callbacks.

## Risks
CSR ordering matters. Restoring stale ring base/head/tail values can corrupt transport queues. TX/RX gap logic must match hardware ring layout. Verification covers selected registers but not every side effect.

## Test Signals
Bank state save/restore across ring-pair reset, transport traffic before/after reset, DMA debug, interrupt coalescing preservation, and failure injection with altered expected status values are useful signals.
