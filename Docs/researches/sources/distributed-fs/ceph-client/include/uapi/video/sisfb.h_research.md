<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/sisfb.h -->
# sources/distributed-fs/ceph-client/include/uapi/video/sisfb.h

Purpose: defines the public ioctl ABI and display flag vocabulary for the SiS framebuffer driver and its companion userspace/X tooling.

Important APIs and types: public flags describe CRT2/LCD/TV/VGA routing, TV standards/interfaces, CRT1/CRT2 display types, and single/mirror/dual-view modes. `sisfb_info` reports card identity, memory heap, mode, version, capabilities, PCI location, panel/TV details, flags, POST state, and reserved expansion bytes. `sisfb_cmd` carries internal command requests/results, and `sis_memreq` supports framebuffer memory allocation/free interfaces. Ioctls include modern `SISFB_GET_INFO*`, retrace, automaximize, TV position, command, lock, and deprecated old numbers.

Control flow: userspace queries info size/info, reads vertical retrace, toggles panning behavior, adjusts TV output position, sends `SISFB_COMMAND`, or locks register access while coordinated tools manipulate state.

State and persistence: runtime state includes current display routing, video memory heap, viewport offset, TV position, lock state, and current flags. Hardware POST, panel delay, EMI, and special timing fields reflect probed hardware state, not persistent kernel data.

Dependencies and integration points: depends on Linux fixed-width types and asm ioctl macros. It integrates with the `sisfb` framebuffer driver, old X drivers, fb memory manager ioctls, and `sisfbctrl`-style utilities.

Risks and test signals: risks include duplicated/aliased flag bits, deprecated ioctl compatibility, large reserved ABI struct layout, command/result validation, and register-lock races. Test old and new ioctls, 32/64-bit layout, TV/LCD routing changes, lock/unlock behavior, and userspace tools expecting exact `SISFB_ID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/sisfb.h -->
