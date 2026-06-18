# sources/distributed-fs/ceph-client/arch/microblaze/lib/uaccess_old.S

Purpose: assembly implementation of `__copy_tofrom_user`, returning the number of bytes not copied on user access fault.

Important APIs and state: global `__copy_tofrom_user(char *to, char *from, int len)` uses r5/r6/r7 and returns r3. Large page-sized aligned copies use unrolled 512-byte chunks and save r19-r25.

Control flow: zero length returns 0. If addresses or count are unaligned, it copies byte-by-byte with exception-table fixups. Aligned non-page copies use a word loop. Exactly page-sized aligned copies use heavily unrolled load/store macros. Fault fixups return the remaining byte count.

State and persistence: mutates destination memory; exception table entries persist in `__ex_table`.

Dependencies and integration: exported through ksyms and consumed by uaccess helpers.

Risks and test signals: the page-sized fast path assumes count equals `PAGE_SIZE` and stack save/restore correctness. Test copy_to/from_user success/fault at every instruction group, unaligned addresses, zero length, and full-page copies.
