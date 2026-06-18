# sources/distributed-fs/ceph-client/samples/rpmsg/Makefile

## Purpose

This Kbuild fragment builds the rpmsg sample client when `CONFIG_SAMPLE_RPMSG_CLIENT` is enabled.

## Important APIs, Types, and Functions

It uses `obj-$(CONFIG_SAMPLE_RPMSG_CLIENT) += rpmsg_client_sample.o`.

## Control Flow

Kbuild includes the object as built-in or module depending on the config value. There is no runtime logic in the Makefile.

## State and Persistence Behavior

Only build state is affected.

## Dependencies and Integration Points

The referenced C file integrates with the rpmsg bus and remote processor channels.

## Risks and Edge Cases

The Makefile assumes Kconfig handles rpmsg dependencies; otherwise compile or link errors occur.

## Test Signals

Enable the config and verify the sample object/module builds.
