# sources/cloud-native/ostree/src/libostree/ostree-repo-finder.h

Purpose: declares the public repository finder interface and result data model used to locate remotes that may provide requested collection refs.

Important APIs/types/functions: `OstreeRepoFinderInterface` with `resolve_async` and `resolve_finish` vfuncs; public wrappers for single and multi-finder resolution; `OstreeRepoFinderResult` with `remote`, `finder`, `priority`, `ref_to_checksum`, `summary_last_modified`, and nullable `ref_to_timestamp`; boxed type and free helpers; `OstreeRepoFinderResultv`.

Control flow: implementers supply async resolution vfuncs returning `GPtrArray` results. Consumers can run one finder or a NULL-terminated array of finders in parallel, then pass results to pull APIs. Result maps indicate which requested refs a remote can provide and the commit checksum/timestamps available for prioritization.

State and persistence: the header defines immutable result objects after construction; maps are ref-counted hash tables and remote/finder references are owned by each result.

Dependencies/integration: includes GIO/GObject, `ostree-ref.h`, `ostree-remote.h`, and `ostree-types.h`. Finder implementations in this group and `ostree-repo-pull.c` are the primary integration points.

Risks: the API relies on pointer-keyed `OstreeCollectionRef` maps with custom hash/equal semantics, so ownership and lifetime must match implementation expectations. Documentation permits `NULL` checksums for advertised-but-not-provided refs; downstream code must handle those.

Test signals: ABI symbols are listed in `libostree-released.sym`; behavior is covered by config finder and find-remotes tests, with more specialized coverage in each backend.
