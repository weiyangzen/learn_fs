## sources/distributed-fs/lizardfs/src/mount/stats.cc

Purpose: implements a hierarchical in-memory counter tree used by mount subsystems and exposed through the stats special file.

Important APIs: `stats_get_subnode` finds or creates child/root nodes by name. `stats_get_counterptr` marks a node active and returns a pointer to its counter. `stats_lock`/`stats_unlock` provide external locking for pointer users. `stats_reset_all` resets non-absolute counters. `stats_show_all` allocates and fills a newline-delimited `fullname: value` buffer. `stats_term` frees the tree.

Control flow/state: nodes are singly linked by first child/next sibling. Active node counts and path lengths estimate the buffer size for printing. Absolute counters survive reset. All tree mutations and printing are guarded by global pthread mutex `glock`.

Dependencies and integration: used by mastercomm, symlink cache, special inode stats, and operation counters elsewhere.

Risks: callers holding counter pointers must use `stats_lock` around increments; the API cannot enforce this. Allocation failure in subnode creation can return null and downstream callers may not always check. `stats_term` does not reset globals after freeing.

Test signals: create nested counters, active/inactive printing, reset behavior with absolute counters, concurrent increments with external lock, and termination cleanup.
