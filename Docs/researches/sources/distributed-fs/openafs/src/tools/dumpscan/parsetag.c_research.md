# sources/distributed-fs/openafs/src/tools/dumpscan/parsetag.c

Purpose: generic tagged-data parser used by dump, volume, and vnode parsing.

Important API: `ParseTaggedData(XFILE *, tagged_field *, unsigned char *tag, tag_parse_info *, void *g_refcon, void *l_refcon)` loops reading one-byte tags, finds them in a field table, reads values according to `DKIND_*`, and invokes optional per-field parser callbacks. `DKIND_SPECIAL` callbacks own stream consumption and return with the next tag in `*tag`.

State/control flow: `tag_parse_info` carries error callback references and recovery state. `TPFLAG_SKIP` skips null tags forward; `TPFLAG_RSKIP` can seek backward after skipped bytes to account for inserted data. String values are freed unless the callback returns `DSERR_KEEP`.

Dependencies/integration: relies on primitive readers and `XFILE` seeking for recovery. All higher-level parsers are table-driven on top of this function.

Risks/test signals: special callbacks must obey the stream contract or the parser desynchronizes. The null-tag recovery is heuristic and should be validated on corrupt dump fixtures. Memory ownership for strings is subtle but explicit through `DSERR_KEEP`.
