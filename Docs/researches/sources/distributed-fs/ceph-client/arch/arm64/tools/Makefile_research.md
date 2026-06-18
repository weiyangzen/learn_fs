# sources/distributed-fs/ceph-client/arch/arm64/tools/Makefile

## Purpose

coordinates generated arm64 architecture headers produced from cpucaps, syscall, HWCAP, and sysreg
description inputs

## Important APIs, Types, and Functions

Source read size: 34 lines, 1004 bytes. Build selections: `kapisyshdr-y -> cpucap-defs.h kernel-
hwcap.h sysreg-defs.h`, `kapi-hdrs-y -> $(addprefix $(kapi)/, $(kapisyshdr-y))`.

## Control Flow and Behavior

Kbuild rules invoke local scripts and generated-header targets before dependent arm64 code is
compiled

## State and Persistence

state is generated header output under the build tree, not runtime kernel state

## Dependencies and Integration Points

depends on AWK/shell generators, source description files, and the kernel generated-header pipeline

## Risks and Test Signals

stale generated headers or missing tool dependencies break arm64 builds; clean rebuilds and
generated header diffs are the test signals
