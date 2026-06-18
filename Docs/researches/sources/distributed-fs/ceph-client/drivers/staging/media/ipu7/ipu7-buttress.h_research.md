# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress.h

## Purpose

This header declares the buttress control API and state structures for IPU7 platform power, IPC, authentication, IRQ, and timestamp services.

## Important APIs, Types, and Functions

`struct ipu_buttress_ctrl` describes subsystem power/frequency/status bits and clock ownership masks. `struct ipu_buttress_ipc` stores CSE IPC completions, NACK data, receive data, and register offsets. `struct ipu_buttress` stores locks, IPC state, cached WDT, frequency knobs, and reference clock. Function prototypes expose power, authentication, frequency, TSC, IRQ, init/exit/restore, CSI port config, and uC wakeup services.

## Control Flow

No implementation flow. The prototypes define the sequence used by bus runtime PM, PCI probe, firmware boot, and ISYS command paths.

## State and Persistence Behavior

The declared structs are embedded in `struct ipu7_device` and persist for the PCI device lifetime.

## Dependencies and Integration Points

It includes completion, IRQ, list, and mutex infrastructure and forward-declares IPU7/device objects. Consumers include bus PM, boot, firmware command, and main PCI code.

## Risks and Edge Cases

Control descriptors must match hardware generation and subsystem. IPC completions and mutexes must be initialized before IRQs can complete them.

## Test Signals

Compile coverage and runtime tests for power/auth/TSC/IRQ helper calls through base and subsystem modules.
