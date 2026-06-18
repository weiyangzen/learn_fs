# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_space.sh

## Purpose
This wrapper runs TPM resource-manager space tests against `/dev/tpmrm0`.

## Important APIs, Types, and Functions
It checks `/dev/tpmrm0`, uses kselftest skip code `4`, and invokes `python3 -m unittest -v tpm2_tests.SpaceTest`.

## Control Flow
The script skips when the resource-manager device is missing and otherwise runs the `SpaceTest` unittest class.

## State and Persistence
The wrapper does not persist state. The underlying tests create and flush TPM transient objects in separate resource-manager spaces.

## Dependencies and Integration Points
It depends on Linux TPM resource manager support and adjacent Python tests.

## Risks
The wrapper checks only device presence, so permission or unsupported command issues are surfaced by Python failures.

## Test Signals
Pass means resource-manager spaces isolate transient handles and return layered command-code errors as expected. Skip means `/dev/tpmrm0` is absent.
