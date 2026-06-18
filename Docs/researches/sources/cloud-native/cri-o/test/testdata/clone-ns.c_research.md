<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/clone-ns.c -->
# sources/cloud-native/cri-o/test/testdata/clone-ns.c

Purpose: C helper fixture for namespace/clone behavior tests.

Important flow: expects one argument, either `with_flags` or `without_flags`. It allocates a 1 MiB stack and calls `clone` with `CLONE_NEWUSER|CLONE_NEWNET` for the flagged mode or zero flags otherwise. The child entry executes `id`.

State and integration: creates a process and potentially new namespaces; no files are persisted. Risks include weak error handling after invalid arguments, pointer arithmetic on `void *` relying on compiler extensions, leaked allocated stack at process exit, and required kernel/userns privileges. Test signal is integration output/exit behavior under CRI-O namespace policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/clone-ns.c -->
