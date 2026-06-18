# sources/distributed-fs/ceph-client/drivers/scsi/scsi_proto_test.c

## Purpose

`scsi_proto_test.c` is a KUnit test suite for selected layout definitions in `<scsi/scsi_proto.h>`. It verifies that packed SCSI protocol structures expose expected bitfields and big-endian fields when overlaid on known byte arrays.

## Important APIs, types, and functions

The single test function `test_scsi_proto()` covers `struct scsi_io_group_descriptor`, `struct scsi_stream_status`, and `struct scsi_stream_status_header`. It uses unions containing the protocol struct and an equally sized byte array, then checks bitfields such as `io_advice_hints_mode`, `st_enble`, `cs_enble`, `ic_enable`, `acdlu`, `rlbsr`, `lbm_descriptor_type`, `perm`, and `rel_lifetime`. Multi-byte protocol fields are checked through `get_unaligned_be16()` and `get_unaligned_be32()`. The suite is registered as `scsi_proto` with `kunit_test_suite()`.

## Control flow

When KUnit runs the suite, it invokes `test_scsi_proto()`. The test initializes constant byte arrays, reads the corresponding struct fields, and issues `KUNIT_EXPECT_EQ()` assertions. It has no setup or teardown and no device interaction.

## State and persistence behavior

The test has no persistent state. All data is static constant test input or local KUnit assertion state. It does not register devices, issue SCSI commands, or alter global SCSI settings.

## Dependencies and integration points

The file depends on KUnit, unaligned big-endian access helpers, and `<scsi/scsi_proto.h>`. It integrates with the kernel KUnit test runner and protects consumers of SCSI protocol structs by catching accidental layout or bitfield-order changes in the public protocol header.

## Risks and edge cases

The test relies on C bitfield layout matching the protocol header's intended representation on supported architectures; bitfields are historically compiler- and endian-sensitive, so this suite is valuable but may need architecture coverage. It covers only a small subset of `scsi_proto.h`; passing this suite does not validate every CDB or descriptor definition. The field name `st_enble`/`cs_enble` is intentionally tested as declared, so spelling changes in the header require coordinated test updates.

## Test signals

Run the KUnit suite named `scsi_proto`. Useful signals are all expectations passing on little-endian and big-endian configurations, plus compile success when `scsi_proto.h` changes. Additional future tests should add more representative byte overlays for other protocol descriptors and CDB structures.
