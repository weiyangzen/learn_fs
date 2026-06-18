# sources/distributed-fs/ceph-client/drivers/s390/cio/ioasm.h

Purpose: declares low-level CIO instruction wrapper functions and pulls in tracepoint definitions for users.

Important APIs/types/functions: declares wrappers for STSCH, MSCH, TSCH, SSCH, CSCH, TPI, CHSC, RSCH, HSCH, XSCH, and STCRW against s390 subchannel, ORB, IRB, TPI, CHSC, and CRW structures.

Control flow: no runtime flow; the header establishes the callable interface implemented by `ioasm.c`.

State and persistence behavior: no state. All state belongs to caller-supplied instruction blocks and hardware.

Dependencies and integration points: included by CIO device, CSS, EADM, QDIO, trace, and machine-check code needing raw channel-subsystem instructions.

Risks and test signals: prototypes must stay synchronized with `ioasm.c` and architecture headers. Compile coverage across all users is the primary signal.
