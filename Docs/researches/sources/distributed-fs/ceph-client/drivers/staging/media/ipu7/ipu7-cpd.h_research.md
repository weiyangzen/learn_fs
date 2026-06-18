# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-cpd.h

## Purpose

This header declares CPD firmware package validation and binary extraction helpers.

## Important APIs, Types, and Functions

It forward-declares `struct ipu7_device` and declares `ipu7_cpd_validate_cpd_file()` plus `ipu7_cpd_copy_binary()`.

## Control Flow

No implementation flow. Callers validate a CPD package before copying named firmware binaries into the uC code region.

## State and Persistence Behavior

No state is owned. Functions operate on caller-provided firmware memory and code-region buffers.

## Dependencies and Integration Points

The header is used by the base IPU7 firmware load path and indirectly by boot/authentication.

## Risks and Edge Cases

Callers must validate before copy and provide a code region large enough for metadata offsets and binary sizes.

## Test Signals

Compile users and firmware-load tests with valid and invalid CPD packages.
