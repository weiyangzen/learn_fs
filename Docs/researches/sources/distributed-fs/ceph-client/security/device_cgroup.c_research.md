# sources/distributed-fs/ceph-client/security/device_cgroup.c

Purpose: implements legacy device cgroup access control and bridges it with cgroup BPF device programs through `devcgroup_check_permission()`.

Important APIs, types, and functions: key types are `enum devcg_behavior`, `struct dev_exception_item`, and `struct dev_cgroup`. It defines cgroup subsystem callbacks `devcgroup_css_alloc()`, `devcgroup_css_free()`, `devcgroup_online()`, `devcgroup_offline()`, files `allow`, `deny`, `list`, and exported `devcgroup_check_permission()`. Internal rule helpers include `match_exception()`, `match_exception_partial()`, `verify_new_ex()`, `revalidate_active_exceptions()`, `propagate_exception()`, and `devcgroup_update_access()`.

Control flow: cgroups inherit parent behavior/exceptions at online time. Writes to `allow`/`deny` parse `a`, `b`, or `c` device rules with major/minor wildcards and access bits, require `CAP_SYS_ADMIN`, enforce parent constraints, update exception lists, and propagate new restrictions down the hierarchy. Permission checks first run BPF cgroup device programs, then legacy list checks under RCU if enabled.

State and persistence: per-cgroup state is `behavior` plus an RCU-protected exception list. Updates are serialized by `devcgroup_mutex`; frees use `kfree_rcu()`. User-visible state is the cgroup v1 devices control files.

Dependencies and integration: integrates with cgroup core, kernfs control files, BPF cgroup device hooks, RCU, capability checks, and device inode permission paths.

Risks and test signals: hierarchy propagation and default-allow/default-deny semantics are subtle. Parser edge cases around wildcards, access bits, and numeric overflow can change containment guarantees. Test signals include parent cannot grant unavailable access, deny propagation to descendants, BPF denial precedence, RCU-safe list reads, and cgroup list output compatibility.
