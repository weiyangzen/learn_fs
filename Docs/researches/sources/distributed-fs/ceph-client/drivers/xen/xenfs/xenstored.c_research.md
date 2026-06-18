<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenstored.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenstored.c

## Purpose
`xenstored.c` exposes dom0 xenstored bootstrap details through xenfs: the shared Xenstore interface address and event channel port.

## Important APIs, types, and functions
It defines `xsd_kva_file_ops` and `xsd_port_file_ops`. Helpers include `xsd_kva_open`, `xsd_kva_mmap`, `xsd_port_open`, `xsd_read`, and `xsd_release`.

## Control flow
Opening `xsd_kva` formats `xen_store_interface` as a string and allows a single-page mmap of that interface via `remap_pfn_range`. Opening `xsd_port` formats `xen_store_evtchn`. Reads use `simple_read_from_buffer`; release frees the per-open string.

## State and persistence
State is per-open `file->private_data` containing a formatted string. The underlying Xenstore page and event channel are kernel runtime Xen state, not filesystem storage.

## Dependencies and integration points
The file depends on Xen page helpers, xenbus globals, VFS file operations, and VM remapping. It integrates with userspace xenstored startup in initial domains.

## Risks and test signals
Risks include unsafe mmap sizes, stale xenstored globals, exposing kernel virtual addresses, and reference/lifetime issues during Xenstore restart. Test signals include read/mmap bounds checks, dom0-only visibility, invalid offsets, and xenstored userspace bootstrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenstored.c -->
