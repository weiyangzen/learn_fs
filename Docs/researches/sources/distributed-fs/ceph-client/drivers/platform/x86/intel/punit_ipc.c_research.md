# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/punit_ipc.c

## Purpose

This file implements the Intel P-Unit IPC mailbox driver used by other platform drivers to issue BIOS, ISP, and GT driver power-management commands through ACPI-provided MMIO resources.

## Important APIs, Types, And Functions

The central state type is `IPC_DEV`, stored globally as `punit_ipcdev`. `intel_punit_ipc_command()` is the exported API. It serializes commands with `ipcdev->lock`, writes optional input data, formats command parameters into the interface register, waits for completion by IRQ or polling, decodes firmware error status, and reads optional output data. `intel_punit_get_bars()` maps required BIOS IPC data/interface resources and optional ISP/GT resources. `intel_punit_ioc()` completes IRQ-driven commands.

## Control Flow

`fs_initcall()` registers the ACPI platform driver early for `INT34D4`. Probe allocates global state, optionally requests an IRQ, maps MMIO bars, initializes the mutex/completion, and leaves the exported API available. Callers encode command type in the command word; the driver selects the mailbox type, handles two-word data for GT/ISP commands, starts the transaction, and blocks until the run bit clears or interrupt completion fires.

## State And Persistence

Runtime state is a singleton device pointer, per-mailbox MMIO base array, one mutex, one completion, and optional IRQ. There is no remove callback and no persistent storage. Hardware mailbox state is transient; command side effects belong to firmware/platform power state.

## Dependencies And Integration Points

The driver depends on ACPI platform enumeration, platform MMIO resources, Linux completion/IRQ APIs, and `asm/intel_punit_ipc.h` for IPC command types and error codes. Legacy telemetry platform code uses this exported command function for PSS telemetry setup and trace controls.

## Risks

There is no explicit NULL check in `intel_punit_ipc_command()` for `punit_ipcdev`, so consumers must load/probe after this early driver. Optional GT/ISP resources may remain NULL; callers issuing those command types on hardware without optional mappings could fault. Polling mode busy-waits up to one second. The singleton design does not support multiple devices.

## Test Signals

Tests should cover ACPI probe, required resource mapping failures, optional resource absence, IRQ and polling completion, timeout behavior, firmware error-code reporting, exported-symbol consumers, and telemetry commands that read/write PSS telemetry registers.
