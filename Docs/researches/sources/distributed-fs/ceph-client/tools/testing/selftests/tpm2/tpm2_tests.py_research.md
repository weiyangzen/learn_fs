# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/tpm2_tests.py

## Purpose
This unittest suite validates TPM2 driver and resource-manager behavior through the local `tpm2.Client`. It covers sealing/unsealing, PCR-bound policies, wrong-auth and wrong-policy failures, malformed command handling, partial reads, TPM spaces, invalid command handling, and nonblocking clients.

## Important APIs, Types, and Functions
`SmokeTest` creates a raw `Client` and root key, then tests auth sealing, PCR policy sealing, wrong auth, wrong PCR policy, too-long auth, too-short commands, partial reads, response overwrite after partial read, and two in-flight command rejection. `SpaceTest` opens `Client.FLAG_SPACE` resource-manager clients to test multiple spaces, flushing, handle visibility, and invalid command RC layering. `AsyncTest` uses `Client.FLAG_NONBLOCK` with and without `FLAG_SPACE`.

## Control Flow
Each smoke test starts with a root key in `setUp()` and flushes it in `tearDown()`. Policy tests create trial sessions to compute policy digests, then real policy sessions to authorize unseal. Wrong-policy mutates a non-policy PCR first to prove success, then mutates a policy PCR to expect failure. Space tests create clients against `/dev/tpmrm0` and inspect handles visible in a specific space. Async tests invoke capability and invalid flush operations through nonblocking reads.

## State and Persistence
The tests create TPM transient objects and sessions and generally flush roots/sessions they own. PCR extension in the policy test mutates PCRs and is persistent until TPM reset/reboot. Log files `SpaceTest.log` and `AsyncTest.log` may be created in the working directory.

## Dependencies and Integration Points
It depends on the local `tpm2.py`, Python unittest, TPM2 hardware or emulator, `/dev/tpm0`, `/dev/tpmrm0`, and resource-manager semantics.

## Risks
PCR mutation can affect later tests and cannot be undone by the suite. Several `try/except: pass` blocks in raw I/O tests can mask unexpected exceptions before assertions check derived variables. Timing and nonblocking behavior depend on driver implementation. TPM dictionary lockout or hierarchy authorization state can affect object creation and unseal outcomes.

## Test Signals
Signals include successful seal/unseal data equality, exact TPM RCs for auth/policy/size/invalid-command failures, correct partial response lengths for `GET_RANDOM`, `IOError` on malformed or concurrent raw commands, per-space handle isolation, and `EINVAL` for invalid nonblocking context flush.
