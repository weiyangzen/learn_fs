# sources/distributed-fs/ceph-client/sound/usb/line6/midibuf.h

## Purpose
Declares the Line 6 MIDI circular buffer type and operations.

## APIs and State
`struct midi_buffer` stores buffer pointer, size, split mode, positions, full flag, and previous command. APIs cover init, reset, destroy, bytes used/free, write, read, and ignore. Read mode constants distinguish transmit and receive behavior.

## Dependencies and Risks
The implementation assumes external synchronization and valid initialized buffers. Callers must choose split mode appropriately: receive buffers generally wait for full messages, transmit buffers can split.

## Test Signals
Unit-style tests for buffer wraparound, full/empty accounting, and MIDI message parsing validate this contract.
