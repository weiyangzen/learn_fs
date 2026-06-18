## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_pagination_bug.c

**Purpose:** Minimal regression test for a `listns` pagination bug where the continuation lookup ignored the requested namespace type filter and could return an ID from the unified tree with the wrong type.

**Important APIs and flow:** The test creates ten children, each running `setup_userns()` and waiting on a socketpair. It calls `sys_listns()` with `ns_type = CLONE_NEWUSER` and a three-entry buffer. If the first batch fills, it sets `req.ns_id` to the last returned ID and requests the next batch. The assertion is simply that the second call succeeds; KASAN or kernel warnings would catch the historical out-of-bounds path.

**State, dependencies, integration:** Child user namespaces are held active by sleeping children. The parent owns the pagination cursor in `req.ns_id`. Dependencies are `../filesystems/utils.h`, `wrappers.h`, and enough permission to create user namespaces. The test integrates directly with `do_listns()` continuation logic.

**Risks and test signals:** A small namespace population may not fill the first batch, reducing coverage. Failure to create user namespaces aborts the test. A pass signals type-filtered pagination can continue from a previous namespace ID without cross-type lookup corruption.
