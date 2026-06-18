# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev6.S

Purpose: implements ARMv6 early data-abort entry handling, normally trusting hardware FSR/FAR data but applying an ARM1136 SWP erratum workaround when configured.

Important APIs/types/functions: exports `v6_early_abort`, reads CP15 FSR/FAR, optionally handles `CONFIG_ARM_ERRATA_326103`, checks processor ID, PSR Java/Thumb bits, decodes ARM instruction including BE8 byte reversal and `teq_ldrd`, disables user access, and branches to `do_DataAbort`.

Control flow: base flow is simple: capture FSR/FAR, disable user access, and dispatch. Under erratum 326103 on ARM1136, ARM-state aborted instructions are read to correct missing write indication for faulty `SWP` handling while preserving `LDRD` as a read.

State and persistence: no persistent state. The erratum path transiently changes FSR bit 11 before entering common abort handling.

Dependencies and integration points: selected by `CPU_ABRT_EV6`. It depends on CP15 registers, processor ID encoding, optional BE8 handling, and common `do_DataAbort`.

Risks: erratum-specific decode must not run on unaffected CPUs or non-ARM states. Incorrect BE8 reversal or `LDRD` handling would corrupt fault classification. The workaround reads faulting instruction memory during abort handling.

Test signals: ARMv6 data-abort tests with and without `CONFIG_ARM_ERRATA_326103`, ARM1136 SWP fault cases, BE8 instruction decoding, and regression tests for normal ARMv6 faults that should bypass the workaround.
