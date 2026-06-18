# sources/distributed-fs/ceph-client/samples/tsm-mr/Makefile

## Purpose

This Kbuild fragment builds the TSM measurement-register sample module.

## Important APIs, Types, and Functions

It maps `obj-$(CONFIG_SAMPLE_TSM_MR) += tsm_mr_sample.o`.

## Control Flow

Kbuild includes the object when the config is enabled.

## State and Persistence Behavior

Only build output is affected.

## Dependencies and Integration Points

The C file depends on the TSM measurement-register framework, miscdevice, and crypto hashing.

## Risks and Edge Cases

Kconfig must provide required dependencies.

## Test Signals

Enable `CONFIG_SAMPLE_TSM_MR` and verify the module builds.
