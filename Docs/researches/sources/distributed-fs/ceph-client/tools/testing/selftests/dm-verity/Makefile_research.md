# sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/Makefile

## Purpose

This Makefile registers the dm-verity keyring shell test with kselftest.

## Important APIs, Types, and Functions

It declares `TEST_PROGS := test-dm-verity-keyring.sh` and includes `../lib.mk`.

## Control Flow

The kselftest framework runs the shell script.

## State and Persistence Behavior

The Makefile has no runtime state; the script loads modules and creates devices.

## Dependencies and Integration Points

It integrates the dm-verity keyring test into the selftest tree.

## Risks and Edge Cases

The runtime script is privileged and destructive enough that accidental execution on a busy dm-verity system may fail module unload or device cleanup.

## Test Signals

Successful packaging makes the shell script available as the dm-verity selftest.
