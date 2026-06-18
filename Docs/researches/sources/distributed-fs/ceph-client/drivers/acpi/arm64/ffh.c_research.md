# sources/distributed-fs/ceph-client/drivers/acpi/arm64/ffh.c

## Purpose
Implements ARM64 architecture callbacks for ACPI FFH operation regions through SMCCC SMC/HVC calls.

## Important APIs, Types, And Functions
Defines `struct acpi_ffh_data`, `acpi_ffh_address_space_arch_setup()`, and `acpi_ffh_address_space_arch_handler()`.

## Control Flow
Setup requires SMCCC 1.2 and a valid SMC or HVC conduit, allocates per-region context, copies ACPI FFH metadata, and stores function pointers for 32-bit and 64-bit calls. The handler validates offset 0 for 32-bit fast calls and offset 1 for 64-bit fast calls, restricts allowed SMCCC owners to standard, SIP, and OEM, copies arguments from the ACPI value buffer, invokes the conduit, and writes results back.

## State And Persistence
Per-region context persists as the ACPI address-space region context until teardown by the ACPI core.

## Dependencies And Integration Points
Depends on ACPI FFH infrastructure, ARM SMCCC version/conduit detection, SMC/HVC call wrappers, and ACPI exception return conventions.

## Risks
Invalid function IDs, wrong call width, excessive length, unsupported SMCCC version, or no conduit all fail with ACPI errors. Owner filtering is important to prevent arbitrary SMCCC calls.

## Test Signals
Test SMCCC version gating, SMC and HVC conduits, 32-bit and 64-bit offsets, owner rejection, length rejection, and result copy-back.
