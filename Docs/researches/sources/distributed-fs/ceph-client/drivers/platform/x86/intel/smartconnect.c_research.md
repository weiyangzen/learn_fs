# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/smartconnect.c

## Purpose

This small ACPI platform driver disables Intel Smart Connect when firmware reports that the operating system has support responsibility.

## Important APIs, Types, And Functions

`smartconnect_acpi_probe()` evaluates ACPI method `GAOS`; if bit 0 is set, it logs a message and executes `SAOS` with value 0. The ACPI match table contains `INT33A0`.

## Control Flow

On platform probe, the driver gets the ACPI handle, reads `GAOS`, returns `-EINVAL` if evaluation fails, and otherwise attempts the disabling write only when the OS-available bit is set. It does not implement remove because it does not maintain state.

## State And Persistence

The driver stores no state. The only persistent behavior is firmware/platform Smart Connect state modified by `SAOS`.

## Dependencies And Integration Points

It depends on ACPI method semantics and Linux platform-driver ACPI matching.

## Risks

If `SAOS` fails, the current code ignores the failure and returns success. There is no rollback or later verification. The driver assumes `GAOS` bit 0 is the only needed policy signal.

## Test Signals

Probe on `INT33A0`, `GAOS` failure handling, log emission when disabling, and firmware-visible `SAOS(0)` execution are the primary signals.
