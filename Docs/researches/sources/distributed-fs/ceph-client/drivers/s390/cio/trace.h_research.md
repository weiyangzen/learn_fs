# sources/distributed-fs/ceph-client/drivers/s390/cio/trace.h

Purpose: declares trace events for s390 CIO instructions, I/O interrupts, adapter interrupts, CHSC calls, and channel report words.

Important APIs/types/functions: event classes include `s390_class_schib` for STSCH/MSCH and `s390_class_schid` for CSCH/HSCH/XSCH/RSCH. Individual events include `s390_cio_tsch`, `s390_cio_tpi`, `s390_cio_ssch`, `s390_cio_chsc`, `s390_cio_interrupt`, `s390_cio_adapter_int`, and `s390_cio_stcrw`. Events copy SCHIB, IRB, ORB, TPI, CHSC request/response, and CRW fields into trace entries.

Control flow: trace macros define payload assignment and printk formatting for instruction wrappers and interrupt code. CHSC tracing copies bounded request and response payloads from the CHSC block.

State and persistence behavior: no driver-owned state. Trace buffers are managed by the kernel tracing subsystem and reflect runtime events only.

Dependencies and integration points: included by `trace.c` and `ioasm.h`; depends on Linux tracepoint infrastructure, s390 UAPI IDs, CIO structures, ORB layouts, and SCSW helper accessors.

Risks and test signals: trace payload copying must avoid overread when CHSC length fields are malformed; the code uses bounded `min_t()` lengths but trusts the response header position. Tests should enable each event, verify formatted fields for representative instruction calls, check trace compile with `TRACE_HEADER_MULTI_READ`, and validate CHSC request/response output.
