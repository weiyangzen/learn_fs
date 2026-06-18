<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx.h

Purpose: Small public interface header for NX accelerator function selection and generic buffer descriptors.

Important APIs and types: Defines `NX_FUNC_COMP_842`, `NX_FUNC_COMP_GZIP`, `__aligned`, `struct nx842_func_args`, `struct nxbuf_t`, and prototypes `nx_function`/`nx_function_end`.

Control flow: No control flow. It gives callers common constants and prototypes for accelerator setup/teardown.

State and persistence: No state is held here; callers own handles and buffers.

Dependencies and integration points: Included by NX gzip and CRB headers. It mirrors older/libnxz-style user API shapes.

Risks: Prototype drift from actual implementation can break builds. Some declarations are broader than the gzip-only implementation in this directory.

Test signals: Compile/link coverage from `gzfht_test` and `gunz_test` validates the used subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx.h -->
