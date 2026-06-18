<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/oradax.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/oradax.h

Purpose: UAPI for Oracle DAX command/completion management.

Important APIs and control flow: defines command codes for kill, info, and dequeue operations; `struct dax_command` passes command type plus completion-area offset; result structures describe kill action, queue state/location, or execution status data. Constants define mmap completion-area length, maximum CCB count, CCB buffer size, device name, submit statuses, CCB states, and kill results.

State, dependencies, and risks: state is DAX hardware/driver command queue and mmapped completion area. Dependencies include Linux integer types, DAX driver ioctl/mmap implementation, and hypervisor state constants noted by comments. Risks are mismatch with hypervisor `HV_CCB_*` values, offset validation into the completion area, and concurrent queue mutation. Test signals are DAX mmap size checks, enqueue/dequeue/kill/info operations, bad-offset rejection, and status propagation from hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/oradax.h -->
