# sources/distributed-fs/ceph-client/drivers/power/reset/macsmc-reboot.c

## Purpose
Apple SMC reset/poweroff driver for Apple Silicon Macs.

## Important APIs, Types, and Functions
SMC command helpers, sys-off poweroff/restart handlers, and platform/MFD child probe.

## Control Flow
probe obtains the parent Apple SMC handle and registers restart/poweroff; callbacks send SMC commands/keys for reset or shutdown and delay while firmware acts.

## State and Persistence Behavior
state is device-managed; SMC firmware owns persistent final power state.

## Dependencies and Integration Points
MFD_MACSMC, platform bus, sys-off API, Apple SMC command interface.

## Risks and Edge Cases
firmware command failures may leave machine running; behavior is model/firmware-specific; handlers need high priority relative to generic fallbacks.

## Test Signals
Apple Silicon shutdown/restart, command failure injection, module bind/unbind, and priority ordering.
