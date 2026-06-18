<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_fork_separation.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_fork_separation.c

Purpose: Tests separation of very large virtual memory areas across fork on 64-bit powerpc. It targets high-address mapping bugs around parent/child address-space handling.

Important APIs and types: Defines `MAP_FIXED_NOREPLACE` fallback, `test()`, and `main()`. Uses high fixed addresses, `mmap`, fork/wait, and memory writes.

Control flow: `test()` maps memory above the usual low address range, forks, lets child and parent modify their views, and checks copy-on-write separation rather than aliasing/corruption.

State and persistence: State is transient VM mappings and forked process status.

Dependencies and integration points: Depends on 64-bit userspace, high virtual address availability, `utils.h`, and COW VM behavior.

Risks: The fallback maps with `MAP_FIXED` on old headers and assumes high addresses are safe. Nonstandard address space limits can cause skips or mapping failures.

Test signals: Pass demonstrates fork does not confuse high virtual mappings or leak writes between parent and child.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_fork_separation.c -->
