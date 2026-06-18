# sources/distributed-fs/coda/coda-src/norton/norton-reinit.cc

Purpose: dump and reload Coda server RVM state for destructive reinitialization. It serializes global volume ID state, volume headers, disk data, vnode records, directory pages, and resolution logs, then reconstructs them into a freshly initialized RVM heap.

APIs and flow: dump mode validates no unskipped backup volumes, writes global state, then iterates volumes and vnodes. Large vnodes include directory inode page counts/refcounts/pages and optional resolution logs. Load mode initializes partitions/server data, reads global state, creates volume headers, reads disk data and logs, attaches volumes, allocates vnodes, copies directory inodes into RVM, rebuilds resolution logs, restores original volume types, frees headers, and truncates the RVM log.

State/persistence: persistent artifact is a flat binary dump file with implicit structure and native in-memory layouts. It directly mutates RVM inside transactions. Risks are high: no portable format/versioning, many full-struct writes with pointers inside, skip logic depends on magic scanning, and load failures can leave partial RVM state. Test signal is successful dump/load under the `reinit` script.
