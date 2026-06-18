# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_smoke.sh

## Purpose
This wrapper runs TPM2 smoke tests for sealing, unsealing, PCR policy, command validation, and partial read behavior.

## Important APIs, Types, and Functions
It checks `/dev/tpm0`, reads `/sys/class/tpm/tpm0/tpm_version_major`, requires version `2`, and invokes `python3 -m unittest -v tpm2_tests.SmokeTest`.

## Control Flow
The script skips if `/dev/tpm0` is missing or if the kernel reports a non-2 TPM version. Otherwise it runs the smoke unittest class.

## State and Persistence
The shell script itself has no persistent state. The Python smoke tests create transient TPM objects, extend PCRs, and flush contexts where possible.

## Dependencies and Integration Points
It depends on sysfs TPM version reporting, Python 3, and adjacent TPM2 helper modules.

## Risks
Smoke tests can alter PCR values, which are not reversible until reboot or reset depending on PCR bank. Device permissions and TPM ownership state can affect results.

## Test Signals
Pass means TPM2 command protocol operations in `SmokeTest` behave as expected. Skip indicates absent or non-TPM2 hardware.
