# sources/distributed-fs/ceph-client/samples/tsm-mr/tsm_mr_sample.c

## Purpose

This module demonstrates exposing emulated Trusted Security Module measurement registers through the `tsm-mr` framework and a misc device.

## Important APIs, Types, and Functions

It defines `sample_report` with several digest buffers, `sample_report_refresh()`, `sample_report_extend_mr()`, `sample_mrs[]`, `sample_tm`, `sample_misc_dev`, init and exit functions. It uses SHA-256/384/512 helpers, `TSM_MR_` macros, flags such as `TSM_MR_F_NOHASH`, `TSM_MR_F_LIVE`, `TSM_MR_F_RTMR`, and `tsm_mr_create_attribute_group()`.

## Control Flow

Init creates a TSM MR attribute group from `sample_tm` and registers a misc device with that group. Reads of live registers can call `refresh`, which recomputes `report_digest` over the report structure before the digest field. Writes/extensions call `sample_report_extend_mr()`, which hashes old MR value plus provided data according to the MR's algorithm. Exit deregisters the misc device and frees the group.

## State and Persistence Behavior

All MR values live in the static `sample_report` structure and persist while the module is loaded. Extending RTMR-capable registers mutates those digest buffers.

## Dependencies and Integration Points

It depends on the TSM MR framework, miscdevice sysfs group support, and kernel crypto SHA helpers.

## Risks and Edge Cases

This is emulated data, not hardware-rooted trust. Unsupported algorithms return `-EOPNOTSUPP`. The copyright year range appears malformed (`2024-2005`) but is not runtime behavior.

## Test Signals

Load the module, inspect misc-device sysfs attributes, read static/live MRs, extend writable RTMRs, and confirm digest changes.
