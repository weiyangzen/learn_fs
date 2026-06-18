# sources/distributed-fs/openafs/src/tools/dumpscan/dump.c

Purpose: serializes dumpscan in-memory records back into AFS dump format.

Important APIs/functions: `DumpDumpHeader`, `DumpVolumeHeader`, and `DumpVNode` emit top-level and attribute tags according to field masks. `DumpVNodeData` writes a `VTAG_DATA` size and caller-provided buffer. `CopyVNodeData` writes a data tag and streams bytes from one `XFILE` to another in 64 KiB chunks. `DumpDumpEnd` writes the dump trailer magic.

State/dependencies: no global state; persistence is whatever is written to the output `XFILE`. It depends on tag constants from `dumpfmt.h`, field masks/types from `dumpscan.h`, network byte-order helper writers from `primitive.c`, and input seeking by callers when copying vnode data.

Risks/test signals: serialization only writes fields whose masks are set, so caller repair/defaulting is responsible for completeness. The `VHTAG_OFFLINE` and `VHTAG_MOTD` paths use `WriteTagInt32` with the first string byte, which looks inconsistent with string parsing and is a risk for repaired dump fidelity. Test signal is successful reparse/restore of generated dumps.
