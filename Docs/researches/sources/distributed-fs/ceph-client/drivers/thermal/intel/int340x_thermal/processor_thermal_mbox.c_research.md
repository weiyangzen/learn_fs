# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_mbox.c

## Purpose

`processor_thermal_mbox.c` implements a serialized MMIO mailbox for Processor Thermal Device commands, mainly workload type request/hint and interrupt configuration.

## Important APIs, Types, and Functions

Exports are `processor_thermal_send_mbox_read_cmd()`, `processor_thermal_send_mbox_write_cmd()`, and `processor_thermal_mbox_interrupt_config()`. `wait_for_mbox_ready()` polls the interface busy bit. Internal read/write helpers program data and command registers at offsets `0x5810` and `0x5818`. A global `mbox_lock` serializes mailbox transactions.

## Control Flow

Each public command locks the mailbox, waits for ready, writes command/data, and waits for ready again. Read commands return either 32-bit workload data or 64-bit data depending on command ID. Interrupt configuration performs read-modify-write on Camarillo interrupt config, optionally updating time-window bits and one enable bit.

## State and Persistence Behavior

Driver state is only the mutex. Hardware mailbox registers hold transient command state and interrupt configuration persists in device registers.

## Dependencies and Integration Points

The mailbox requires PCI drvdata to be `struct proc_thermal_device` with valid `mmio_base`. It is called by workload request, workload hint, RFIM mailbox attributes, and power-floor configuration.

## Risks and Test Signals

Risks include busy polling without delay, returning the last `ret` value if the retry loop exhausts, global serialization across devices, and command-specific 32/64-bit response assumptions. Test signals include busy mailbox failure, read/write command success, interrupt config enable/disable/time-window update, and concurrent sysfs users.
