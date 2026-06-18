<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recle.cc -->
# sources/distributed-fs/coda/coda-src/resolution/recle.cc

Purpose: implements recoverable resolution log entries (`recle`) stored in RVM and their serialization/printing.

Important APIs/control flow: constructor/destructor abort because `recle` entries are allocated as raw RVM slots, not normal C++ objects. `InitFromsle` marks the fixed record and allocates a `recvarl` variable part according to opcode, copying payload from an initialized transient `rsle`. `FreeVarl` destroys the variable payload transactionally. `HasList` returns nested child logs for removed directories and rename-deleted directory targets. `GetDumpSize` and `DumpToBuf` serialize fixed and variable parts with begin/end stamps and word alignment. `print` dispatches payload-specific formatting.

State/persistence: fixed fields (`serverid`, `storeid`, `opcode`, directory fid, size, `vle`, index, seqno) live in recoverable memory; variable payloads are separate recoverable allocations. RVM range marking is explicit.

Dependencies/integration: used by `ops.cc`, `recov_vollog.cc`, `rsle` parsing, and remote log shipment. Depends on `rvmlib`, `recvarl`, opcode constants from `resutil`, and payload types declared in `recle.h` with methods implemented in `ops.cc`.

Risks/test signals: `DumpToBuf` copies `vle->vfld` even when `size == 0` and `vle == NULL`, which is risky for `ResolveNULL_OP`/`RES_Repair_OP`. Opcode additions require synchronized changes. Test dumping null-payload records, each variable payload, nested child logs, and recovery after transaction abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recle.cc -->
