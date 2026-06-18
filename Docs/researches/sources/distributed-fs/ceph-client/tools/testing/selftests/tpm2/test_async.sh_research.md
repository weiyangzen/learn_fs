# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_async.sh

## Purpose
This wrapper runs TPM2 asynchronous/nonblocking unittest coverage when both the raw TPM and resource-manager devices are present.

## Important APIs, Types, and Functions
The script checks `/dev/tpm0` and `/dev/tpmrm0`, defines kselftest skip code `4`, and invokes `python3 -m unittest -v tpm2_tests.AsyncTest`.

## Control Flow
It exits skip if either required device node is missing. Otherwise it runs the `AsyncTest` unittest class and forwards combined output.

## State and Persistence
The script does not persist state; Python tests open TPM device files and close them.

## Dependencies and Integration Points
It depends on TPM2 character devices, Python 3, and adjacent `tpm2.py`/`tpm2_tests.py`.

## Risks
Device-node existence does not guarantee a TPM2 implementation or permission. Nonblocking behavior can vary with driver/resource-manager state.

## Test Signals
Pass means the `AsyncTest` unittest class succeeds. Exit code 4 means the environment lacks required TPM devices.
