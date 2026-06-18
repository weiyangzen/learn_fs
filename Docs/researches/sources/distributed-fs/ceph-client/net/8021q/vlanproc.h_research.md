<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlanproc.h -->
# sources/distributed-fs/ceph-client/net/8021q/vlanproc.h

This header declares the VLAN procfs integration points and provides no-op stubs when procfs is disabled. With `CONFIG_PROC_FS`, it exposes `vlan_proc_init()`, `vlan_proc_rem_dev()`, `vlan_proc_add_dev()`, and `vlan_proc_cleanup()`.

The header does not hold state itself. It controls compile-time integration between the main VLAN module and `vlanproc.c`, allowing callers to invoke proc helpers unconditionally.

Risks are limited to configuration mismatches: stubs must preserve caller semantics and return success for add/init when procfs is disabled. Tests should compile VLAN with and without procfs and verify callers do not need conditional code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlanproc.h -->
