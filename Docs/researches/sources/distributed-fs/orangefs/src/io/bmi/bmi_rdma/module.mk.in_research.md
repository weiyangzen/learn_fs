# sources/distributed-fs/orangefs/src/io/bmi/bmi_rdma/module.mk.in

## Purpose
Makefile fragment that includes the OrangeFS BMI RDMA transport sources in selected build products when configure enables RDMA support.

## Important APIs, Types, And Functions
The fragment is gated by `BUILD_RDMA`. It sets `DIR := src/io/bmi/bmi_rdma`, declares `cfiles := rdma.c util.c mem.c`, expands `src`, appends those files to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`, and adds the configured RDMA include directory to `rdma.c` through `MODCFLAGS_$(DIR)/rdma.c := -I@RDMA_INCDIR@`.

## Control Flow
During generated makefile evaluation, no RDMA files are added unless `BUILD_RDMA` is non-empty. When enabled, all three RDMA method implementation files become part of the library, server, and BMI library source sets. Only `rdma.c` receives the explicit RDMA include path; `util.c` and `mem.c` rely on local/project headers or transitive include paths.

## State And Persistence
No runtime state is defined. The persistent effect is build metadata that controls whether the RDMA BMI method is compiled and which include path is used for provider headers.

## Dependencies And Integration Points
The fragment depends on configure substitutions `BUILD_RDMA` and `@RDMA_INCDIR@`, top-level source-list variables, and OrangeFS module makefile conventions. It integrates `rdma.c`, `util.c`, and `mem.c` into the same BMI method build.

## Risks And Test Signals
If RDMA headers are needed by more than `rdma.c`, limiting `-I@RDMA_INCDIR@` to that file can cause build failures after include changes. Stale configure values can silently compile against the wrong provider headers. Build tests should cover RDMA disabled, RDMA enabled with valid include directory, and dependency tracking for all three RDMA source files.
