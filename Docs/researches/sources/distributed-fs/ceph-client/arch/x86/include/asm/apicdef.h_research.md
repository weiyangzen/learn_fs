
# sources/distributed-fs/ceph-client/arch/x86/include/asm/apicdef.h

Purpose: symbolic register map and bit definitions for local APIC, IO-APIC base addresses, delivery modes, xAPIC/x2APIC enable bits, and APIC ID layout.

Important APIs and control flow: this file exports register offsets such as `APIC_ID`, `APIC_EOI`, `APIC_ICR`, LVT registers, timer divisor fields, ESR bits, interrupt command bits, and helper macros like `GET_APIC_VERSION()`, `GET_APIC_MAXLVT()`, `GET_XAPIC_DEST_FIELD()`, and `SET_APIC_DELIVERY_MODE()`. It also fixes `MAX_IO_APICS`, `MAX_LOCAL_APIC`, `BAD_APICID`, and cluster/CPU extraction macros by word size.

State, dependencies, and risks: it has no runtime state, but its constants bind APIC register programming throughout interrupt, SMP, and timer code. Dependencies are `linux/bits.h`, fixmap `APIC_BASE`, and configuration width. Risks are off-by-bit errors, using xAPIC-only encodings in x2APIC paths, and assuming APIC ID limits that differ between 32-bit and 64-bit builds. Test signals are APIC bringup, interrupt routing, timer calibration, and KVM/APIC emulation compatibility.
