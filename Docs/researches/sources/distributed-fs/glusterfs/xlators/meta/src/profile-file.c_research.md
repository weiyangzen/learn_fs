# sources/distributed-fs/glusterfs/xlators/meta/src/profile-file.c

Purpose: implements the virtual `profile` file under each xlator, exposing profiling counters through Gluster's statedump profile formatter.

Important APIs/types/functions: `profile_file_fill()` calls `gf_proc_dump_xlator_profile(xl, strfd)` for the xlator stored in inode context. `meta_profile_file_hook()` attaches `profile_file_ops` and propagates parent context.

Control flow: lookup of `profile` beneath an xlator directory binds that xlator. Reads invoke the profile dump and cache the generated text per fd.

State and persistence behavior: no state is persisted; output is a snapshot of volatile profile counters at first read.

Dependencies and integration points: depends on statedump/profile support and `xlator-dir.c` fixed entries. The output quality depends on profiling instrumentation in the target xlator.

Risks and edge cases: profile data may be large or change rapidly. Long-lived fd caching can hide updates. Missing context causes unsafe dereference.

Test signals: read profile for active translators, compare with enabled profiling counters, and test behavior when profiling data is absent or zero.
