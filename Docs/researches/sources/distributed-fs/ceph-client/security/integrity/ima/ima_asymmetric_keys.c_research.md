<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_asymmetric_keys.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_asymmetric_keys.c

## Purpose
Measures asymmetric key payloads when keys are created or updated, allowing IMA policy to record key material linked to configured keyrings.

## Important APIs, Types, And Functions
- `ima_post_key_create_or_update()` is the LSM key hook implementation for asymmetric-key measurement.

## Control Flow
The hook ignores non-asymmetric keys and empty payloads. If early boot key queueing is active, it attempts to queue the key payload. Otherwise it calls `process_buffer_measurement()` using the keyring description as both event name and policy `func_data` for `KEY_CHECK`.

## State And Persistence
This file does not own persistent state. Measurements become IMA measurement-list entries, and early keys may be temporarily stored by the key queue subsystem until policy is ready.

## Dependencies And Integration Points
Depends on key subsystem types, `key_type_asymmetric`, optional early boot key queueing helpers, and the generic IMA buffer measurement path. Policy can select keyrings by name through the keyring description passed as function data.

## Risks And Edge Cases
Null keyrings or unexpected missing descriptions would affect event naming. Measurements are policy-dependent and can be skipped if no rule matches. Queuing is important before policy initialization; lost queueing would miss early key measurements.

## Test Signals
Create or update asymmetric keys in measured keyrings, then inspect the IMA measurement list for `KEY_CHECK` events named after the keyring. Test early boot queueing by loading keys before policy processing completes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_asymmetric_keys.c -->
