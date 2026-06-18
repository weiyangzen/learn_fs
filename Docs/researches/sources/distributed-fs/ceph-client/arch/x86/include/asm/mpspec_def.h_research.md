# sources/distributed-fs/ceph-client/arch/x86/include/asm/mpspec_def.h

## Purpose
Defines the packed Intel MP Specification 1.1/1.4 table structures and constants used by x86 MP table parsers.

## Important APIs, Types, And Functions
Defines `SMP_MAGIC_IDENT`, `MPC_SIGNATURE`, entry type constants `MP_PROCESSOR`, `MP_BUS`, `MP_IOAPIC`, `MP_INTSRC`, `MP_LINTSRC`, and `MP_TRANSLATION`, CPU flags, bus type strings, APIC flags, IRQ polarity/trigger masks, `MP_APIC_ALL`, `MPC_OEM_SIGNATURE`, `enum mp_irq_source_types`, `enum mp_bustype`, and structures `mpf_intel`, `mpc_table`, `mpc_cpu`, `mpc_bus`, `mpc_ioapic`, `mpc_intsrc`, `mpc_lintsrc`, and `mpc_oemtable`.

## Control Flow
The parser reads the floating pointer structure, validates signatures/checksums, then walks entries by type using these layouts to build CPU, bus, IOAPIC, and interrupt-source state.

## State And Persistence
No runtime state is owned here. The structs describe firmware memory that is consumed at boot.

## Dependencies And Integration Points
Integrated with `mpspec.h`, early SMP parsing, IOAPIC setup, and legacy firmware compatibility.

## Risks And Edge Cases
Field sizes and order are firmware ABI and cannot drift. Checksum/signature constants must match the spec. Unexpected OEM or translation entries require parser-side bounds handling.

## Test Signals
MP table parser tests, booting ACPI-disabled legacy SMP guests, fuzzed MP table parsing, and 32-bit `MAX_MPC_ENTRY` build coverage are useful.
