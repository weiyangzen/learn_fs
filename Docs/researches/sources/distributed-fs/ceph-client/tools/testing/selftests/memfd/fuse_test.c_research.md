# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/fuse_test.c

Purpose: tests memfd sealing interactions with get_user_pages by racing FUSE direct-IO reads into a mapped memfd against `F_ADD_SEALS`.

Important APIs/types/functions: uses `sys_memfd_create`, `ftruncate`, `mmap`, `read`, `clone(CLONE_FILES|CLONE_FS|CLONE_VM)`, `F_GET_SEALS`, `F_ADD_SEALS`, `F_SEAL_WRITE`, and optional `hugetlbfs` mode.

Control flow: opens the slow FUSE file, creates and maps a sealable memfd, spawns a sealing thread that waits 200ms, unmaps the shared mapping, tries to add `F_SEAL_WRITE` while the parent read should have pages pinned, then retries after the read completes if needed. Parent reads from the FUSE file into the mapped memfd, checks whether sealing happened before/after data transfer, joins the sealing thread, and verifies final seal state and content behavior.

State and persistence: process-global `global_mfd` and `global_p` share state with the clone child. No persistent files except FUSE mount inputs.

Dependencies and integration points: requires `fuse_mnt` mounted path, memfd sealing, GUP behavior, and optionally free huge pages for hugetlbfs mode.

Risks: timing depends on FUSE delay and scheduler. Test intentionally tolerates future kernels that avoid EBUSY by replacing pages.

Test signals: aborts on unexpected syscall/seal/content outcomes; prints `fuse: DONE` on success.
