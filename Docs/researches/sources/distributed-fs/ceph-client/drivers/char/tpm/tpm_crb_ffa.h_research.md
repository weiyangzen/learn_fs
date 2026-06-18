# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb_ffa.h

## Purpose
Provides the small integration contract between the generic TPM CRB driver and the optional Arm FF-A CRB start-method driver.

## Important APIs, Types, And Functions
Declares `tpm_crb_ffa_init()` and `tpm_crb_ffa_start()` when `CONFIG_TCG_ARM_CRB_FFA` is reachable, otherwise supplies no-op inline stubs returning success. It also defines `CRB_FFA_START_TYPE_COMMAND` and `CRB_FFA_START_TYPE_LOCALITY_REQUEST`.

## Control Flow
The header lets CRB code call initialization and start notifications unconditionally while compile-time configuration determines whether real FF-A work occurs. Request-type constants select whether the secure TPM service should process a CRB command or a locality request.

## State And Persistence
The header owns no state. The real state resides in `tpm_crb_ffa.c`; stub builds intentionally persist no FF-A status.

## Dependencies And Integration Points
Used by CRB code that needs to support ACPI TPM2 FF-A start methods without hard-linking to the FF-A implementation in disabled configurations.

## Risks And Edge Cases
No-op stubs mean callers must rely on platform detection to avoid silently treating an unavailable FF-A start method as initialized. Constants must remain synchronized with the FF-A ABI documentation and `tpm_crb_ffa.c`.

## Test Signals
Build matrix coverage with FF-A enabled, module-only, built-in, and disabled configurations; CRB start-method tests for both command and locality request qualifiers.
