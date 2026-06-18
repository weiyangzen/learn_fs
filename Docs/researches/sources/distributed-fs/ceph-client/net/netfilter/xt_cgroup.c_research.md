# sources/distributed-fs/ceph-client/net/netfilter/xt_cgroup.c

Purpose: `cgroup` match selects packets by socket cgroup classid or cgroup path ancestry.

Important APIs/types/functions: `cgroup_mt_check_v0/v1/v2()`, `cgroup_mt_v0/v1/v2()`, destroy helpers, `cgroup_get_from_path()`, and socket cgroup accessors.

Control flow: check validates inversion flags, requires exactly one of path/classid for newer revisions, checks net_cls availability, resolves cgroup path, and stores hidden cgroup pointer. Runtime requires a full socket in the same netns, then tests classid equality or cgroup descendant relation with inversion.

State and persistence: path rules hold cgroup references; classid rules hold config only. Dependencies include socket cgroup data, cgroup core, optional net_cls, x_tables, and local in/out/postrouting hooks. Risks: packets without sockets never match, netns mismatch, cgroup ref lifetime, classid config dependence, and usersize hiding. Test signals: revisions 0-2, classid disabled, path invalid, inversion, no socket, descendant match, and destroy `cgroup_put()`.
