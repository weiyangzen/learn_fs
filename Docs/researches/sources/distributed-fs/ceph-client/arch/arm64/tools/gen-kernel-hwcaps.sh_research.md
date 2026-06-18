# sources/distributed-fs/ceph-client/arch/arm64/tools/gen-kernel-hwcaps.sh

## Purpose

generates kernel HWCAP metadata headers from arm64 CPU feature descriptions

## Important APIs, Types, and Functions

Source read size: 23 lines, 545 bytes.

## Control Flow and Behavior

the shell pipeline invokes the arm64 sysreg/hwcap generation tooling and forwards arguments from
Kbuild

## State and Persistence

it has no persistent runtime state beyond generated header files

## Dependencies and Integration Points

integrates with arch/arm64/tools/Makefile and ELF HWCAP reporting used by cpu feature and userspace
capability paths

## Risks and Test Signals

script portability, input ordering, and regenerated constants are the risk points; test signals are
clean header regeneration and boot-time HWCAP exposure
