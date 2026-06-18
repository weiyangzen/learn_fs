# sources/distributed-fs/ceph-client/include/linux/hp_sdc.h

## Purpose
`hp_sdc.h` defines the HP i8042 System Device Controller interface used on legacy HP systems for timer, HIL, cooked keyboard, RTC/beeper, and controller register access. It describes IRQ hook registration, queued SDC transactions, action flags, status/command/register constants, and the `hp_i8042_sdc` runtime state.

## Important APIs, Types, And Functions
Public callback type `hp_sdc_irqhook` receives irq, device ID, status, and data. Registration helpers request/release timer, HIL, and cooked IRQ hooks. `hp_sdc_transaction` describes queued command/data sequences with callback or semaphore completion. Queue APIs are `__hp_sdc_enqueue_transaction()`, `hp_sdc_enqueue_transaction()`, and `hp_sdc_dequeue_transaction()`. `hp_i8042_sdc` stores locks, IRQ/NMI lines, IO ports, interrupt mask, controller register cache, hook pointers, transaction queue, read/write progress, device pointer, kicker timer, and tasklet.

## Control Flow And State
Clients enqueue transactions consisting of atomic acts. The SDC driver serializes command/data register access, handles status interrupts, calls hooks in IRQ/tasklet context, signals semaphores for synchronous transactions, and uses a tasklet/timer kicker to keep progress moving. State persists in interrupt masks, pending transaction queue, current read/write indices, cached i8042 registers, hook lists, and architecture device registration data.

## Dependencies And Integration Points
It depends on interrupt, timer, time, types, and HPPA or m68k architecture device support. It integrates with HP-HIL MLC, keyboard input, timer/RTC/beeper support, and low-level IO port access.

## Risks
Risks include transaction queue overflow, action flag misuse such as combining data input with deallocation in one act, interrupt mask races, IBF polling timeout, tasklet/use-after-free during unregister, and architecture guard failures on unsupported platforms. Hook callbacks may run in interrupt or tasklet context and must not sleep.

## Test Signals
Test IRQ hook register/release, synchronous and callback transactions, dequeue/cancel, HIL command/data routing, timer status interrupts, RTC/beeper commands, IBF timeout handling, queue full behavior, and probe/build on supported HPPA/m68k configurations.
