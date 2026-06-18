# sources/distributed-fs/ceph-client/drivers/s390/cio/orb.h

Purpose: defines packed operation-request-block layouts for command-mode, transport-mode, and EADM subchannel starts.

Important APIs/types/functions: `struct cmd_orb`, `struct tm_orb`, `struct eadm_orb`, and `union orb` model the architecture fields passed to SSCH, including interrupt parameter, storage key, path mask, mode flags, CCW/TCW/AOB address, priority, compatibility bits, and format fields.

Control flow: no executable flow; instances are filled by CIO, CCW, QDIO, FCX, and EADM code and passed to `ssch()`.

State and persistence behavior: ORBs are transient in-memory hardware command blocks, aligned and packed for architecture consumption.

Dependencies and integration points: used by `io_sch.h`, `ioasm.c`, `eadm_sch.c`, low-level CIO start helpers, and any code starting command or transport I/O.

Risks and test signals: bitfield layout, packing, alignment, and DMA address width are ABI-critical. Tests are architecture compile/runtime coverage of command-mode start, transport-mode start, EADM start, and tracepoint copying of ORB data.
