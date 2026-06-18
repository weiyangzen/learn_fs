# sources/distributed-fs/ceph-client/drivers/message/Makefile Research

## Purpose
This Makefile is the build entry point for MPT-based message-passing device drivers.

## Important APIs, Types, And Functions
It contains one build rule: `obj-$(CONFIG_FUSION) += fusion/`, which descends into the Fusion MPT subdirectory when the `FUSION` menuconfig is enabled.

## Control Flow
There is no runtime logic. Kbuild uses the `CONFIG_FUSION` value to decide whether to enter `drivers/message/fusion/`.

## State And Persistence
The file only contributes build-time state derived from kernel configuration.

## Dependencies And Integration Points
It integrates the message driver subtree with the broader kernel build. The downstream `fusion/Kconfig` and `fusion/Makefile` define actual driver symbols and objects.

## Risks
Because `FUSION` is a bool gate with no object itself, disabling it hides all nested Fusion drivers. Misconfigured parent Kconfig inclusion would silently omit all MPT drivers.

## Test Signals
Verify `CONFIG_FUSION=n` skips the directory and `CONFIG_FUSION=y` descends into it, then build selected Fusion children as modules and built-ins.
