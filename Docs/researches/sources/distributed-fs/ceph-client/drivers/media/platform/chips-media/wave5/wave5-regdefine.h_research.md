# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-regdefine.h

## Purpose
`wave5-regdefine.h` is the register and firmware mailbox ABI definition for Wave5 hardware. It names command ids, query options, common registers, decoder mailboxes, encoder mailboxes, reset bits, remap controls, product registers, interrupt registers, GDI/backbone bus registers, and result fields.

## Important APIs and Constants
The file defines `enum W5_VPU_COMMAND` for firmware commands such as init, wake, sleep, create/destroy instance, init sequence, set framebuffer, picture run, query, and bitstream update. `enum query_opt` describes query modes including VPU info, results, display flag update, bitstream pointer operations, and debug info. Macro groups cover power/debug registers, FIO, interrupts, reset, remap, busy status, product identification, command/result status, bitstream options, common create-instance registers, set-framebuffer registers, decoder sequence/result registers, encoder sequence/set-param/picture/result registers, and bandwidth report registers.

## Control Flow and Integration
The header is consumed by `wave5-hw.c` and VDI code. Firmware command flow depends on writing command-specific arguments into shared offsets, issuing `W5_COMMAND`, then reading success, fail reason, queue status, and command-specific return registers. Many offsets intentionally overlap because the firmware interprets them based on the active command or query option.

## State and Persistence
The macros describe hardware-visible state. Registers persist across command phases until firmware, reset, or host code changes them. The definitions include state for firmware code remapping, VCPU program counter, interrupts, framebuffers, stream pointers, decoder display flags, encoder source buffers, rate control, and performance ticks.

## Dependencies and Risks
The header depends on Linux `BIT()` and register users including it in a context where bit helpers are available. Risks are ABI mismatch with firmware, wrong command context for an overlapping offset, missing product-specific differences, and comments for unsupported or unused registers becoming stale.

## Test Signals
Test by booting firmware, querying product info, running decoder and encoder init/picture/result commands, validating interrupt reason bits, exercising reset and sleep/wake, and comparing register programming against vendor documentation or known-good traces.
