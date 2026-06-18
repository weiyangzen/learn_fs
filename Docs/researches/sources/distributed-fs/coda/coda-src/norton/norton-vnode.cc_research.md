# sources/distributed-fs/coda/coda-src/norton/norton-vnode.cc

Purpose: implements vnode inspection and targeted vnode repair commands for Norton.

APIs and flow: `PrintVnodeDiskObject` prints vnode disk fields and version vectors. `show_vnode` either finds small vnodes by uniquifier or prints a specific vnode by volume/vnode/unique. `show_free` scans small/large RVM free lists for null, nonzero, and duplicate entries. `set_linkcount` wraps `setcount`, which starts an RVM transaction, extracts the vnode, changes `linkCount`, replaces the vnode, and commits.

State/dependencies: reads and mutates RVM vnode state through volume/index/recov APIs and resolution log printers. Risks include unsigned `count < 0` check being ineffective, no higher-level consistency checks when setting link counts, and free-list inspection relying on raw memory comparison. Test signal is manual `show vnode`, `show free`, and `set linkcount` usage.
