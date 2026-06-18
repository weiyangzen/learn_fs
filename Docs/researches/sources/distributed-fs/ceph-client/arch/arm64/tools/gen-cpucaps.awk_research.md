# sources/distributed-fs/ceph-client/arch/arm64/tools/gen-cpucaps.awk

## Purpose

generates arm64 CPU capability constants from a sorted textual capability list

## Important APIs, Types, and Functions

Source read size: 40 lines, 773 bytes. Functions: `fatal`.

## Control Flow and Behavior

the AWK script validates numbering/order, emits C preprocessor defines, and terminates through
fatal() on malformed input

## State and Persistence

state is limited to AWK counters while generating a header during the build

## Dependencies and Integration Points

integrates with arch/arm64/tools/Makefile and generated asm/cpucaps.h consumers in cpufeature code

## Risks and Test Signals

bad sorting or duplicate capability names shift feature-bit ABI inside the kernel; build
regeneration and cpufeature compilation are the test signals
