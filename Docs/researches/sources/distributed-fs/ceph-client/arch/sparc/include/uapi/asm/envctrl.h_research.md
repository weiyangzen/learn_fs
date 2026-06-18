<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/envctrl.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/envctrl.h

Purpose: User ABI definitions for SPARC environmental-control devices.

Important APIs and control flow: the header defines ioctl commands and data structures for reading environmental status such as fan, power-supply, temperature, and global warning/shutdown conditions. It also encodes device/status constants used by user monitoring tools and platform drivers.

State, dependencies, and risks: persistent state is sensor and controller hardware state. Dependencies include the envctrl driver, ioctl ABI, and platform-specific sensor layout. Risks include structure-size compatibility, interpreting advisory warning bits as control policy, and stale platform constants for rare Sun hardware. Test signals are sensor ioctl enumeration, threshold alarm simulation where possible, and userspace monitoring compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/envctrl.h -->
