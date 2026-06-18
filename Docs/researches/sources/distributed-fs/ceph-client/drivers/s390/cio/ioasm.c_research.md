# sources/distributed-fs/ceph-client/drivers/s390/cio/ioasm.c

Purpose: wraps s390 channel-subsystem machine instructions in C helpers with condition-code normalization, tracepoint emission, and limited exception handling.

Important APIs/types/functions: exported or local wrappers include `stsch()`, `msch()`, `tsch()`, `ssch()`, `csch()`, `tpi()`, `chsc()`, `rsch()`, `hsch()`, `xsch()`, and `stcrw()`. Internal `__*` helpers issue inline assembly and return transformed condition codes; STSCH/MSCH/SSCH/CHSC use exception-table recovery for operand exceptions.

Control flow: each public wrapper calls the assembly helper, emits the matching `trace_s390_cio_*` tracepoint, and returns the condition code or `-EIO` on trapped exception for helpers that can trap. `stcrw()` optionally consumes injected CRWs when `CONFIG_CIO_INJECT` is enabled before falling back to the hardware instruction.

State and persistence behavior: functions do not own persistent state. They read or write caller-provided architecture blocks such as SCHIB, IRB, ORB, CHSC area, TPI info, and CRW.

Dependencies and integration points: used by nearly all CIO/CSS layers. Depends on s390 inline assembly constraints, `asm-extable`, trace definitions, `cio_inject`, `orb.h`, and architecture status structures.

Risks and test signals: register clobber lists and condition-code transformation are architecture-critical. `__ssch()` initializes an exception variable but ignores it, returning the condition code path even on exception, which deserves scrutiny against architectural guarantees. Tests require s390 build/boot coverage, tracepoint validation, CHSC exception handling, CRW injection, and instruction return-code mapping for not-operational/status-pending/busy cases.
