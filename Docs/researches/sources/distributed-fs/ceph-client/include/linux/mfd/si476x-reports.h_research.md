# sources/distributed-fs/ceph-client/include/linux/mfd/si476x-reports.h

## Purpose

This 154-line header defines packed report structures returned by Si476x debug and command paths for received signal quality, audio/control filtering, AGC, and RDS block counts.

## Important APIs, Types, and Functions

It defines packed `struct si476x_rsq_status_report`, `struct si476x_acf_status_report`, `enum si476x_fmagc`, `struct si476x_agc_status_report`, and `struct si476x_rds_blockcount_report`.

## Control Flow

No flow executes. Command implementations fill these structures from raw device responses, and debugfs/V4L2 code interprets the decoded fields.

## State and Persistence Behavior

The structs are transient snapshots of tuner measurements: RSSI, SNR, multipath, AFC, antenna capacitance, RDS PI, blend/hicut/softmute, AGC gains, and RDS counts. They do not persist after the caller consumes them.

## Dependencies and Integration Points

It integrates Si476x command code with debugfs, V4L2 status reporting, and RDS/statistics consumers. Packed layout preserves command response ABI.

## Risks and Edge Cases

Packed layouts must match device response order and signedness. Several fields are poorly documented, so consumers should avoid inferring more than the command API guarantees.

## Test Signals

Response decoding tests using captured command bytes, packed-size checks, debugfs read tests, and V4L2 signal-quality reporting tests.
