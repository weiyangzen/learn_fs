# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/Makefile

## Purpose

This Makefile builds the `udmabuf` driver selftest under the drivers/dma-buf selftest area.

## Important APIs, Types, and Functions

It sets `CFLAGS += $(KHDR_INCLUDES)`, declares `TEST_GEN_PROGS := udmabuf`, sets `top_srcdir ?=../../../../..`, and includes `../../lib.mk`.

## Control Flow

Kselftest builds the `udmabuf` C test. Although this work item maps only the Makefile and config, the generated program tests `/dev/udmabuf`.

## State and Persistence Behavior

The Makefile stores build metadata only.

## Dependencies and Integration Points

It integrates exported kernel headers and kselftest library rules for driver tests.

## Risks and Edge Cases

Incorrect `top_srcdir` can break include resolution in out-of-tree builds. Missing udmabuf support causes runtime skips rather than build failures.

## Test Signals

Build success produces the `udmabuf` executable for the selftest run.
