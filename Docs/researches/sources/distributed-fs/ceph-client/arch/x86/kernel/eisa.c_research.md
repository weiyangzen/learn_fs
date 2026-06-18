# sources/distributed-fs/ceph-client/arch/x86/kernel/eisa.c

## Purpose
Detects legacy EISA bus presence on x86 by checking the EISA signature in low physical memory.

## Important APIs, Types, And Functions
`eisa_bus_probe()` maps physical address `0x0FFFD9`, checks for the four-byte `"EISA"` signature, and sets global `EISA_bus`. It is registered with `subsys_initcall()`.

## Control Flow
The probe skips non-initial Xen PV domains and SEV-SNP guests. Otherwise it maps the signature location write-back, compares the little-endian signature, sets `EISA_bus` if matched, unmaps, and returns success.

## State, Persistence, And Dependencies
Persistent state is the global `EISA_bus` flag. It depends on `memremap()`, Xen domain checks, confidential-computing attributes, and EISA core state.

## Integration Points
Allows legacy EISA subsystem probing only when the platform signature exists and is safe to access.

## Risks
Reading legacy physical addresses can be invalid in virtual or confidential guests, so explicit skips matter. Mapping failure currently still calls `memunmap(p)` with a possibly null pointer expectation based on kernel API tolerance.

## Test Signals
Real or emulated EISA machines should set `EISA_bus=1`; Xen PV non-dom0 and SNP guests should skip probing without faults.
