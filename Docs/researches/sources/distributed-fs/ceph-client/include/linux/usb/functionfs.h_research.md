<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/functionfs.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/functionfs.h

Purpose: kernel wrapper that exposes FunctionFS UAPI definitions to kernel code.

Important APIs and types: this header defines no new symbols; it includes `<uapi/linux/usb/functionfs.h>`.

Control flow: FunctionFS implementation and gadget code include this wrapper when they need descriptor/event/ioctl constants shared with userspace.

State and persistence: no state is stored here. Runtime FunctionFS state lives in the FunctionFS filesystem and gadget function implementation.

Dependencies and integration points: integrates kernel FunctionFS code with the UAPI contract used by userspace gadget daemons.

Risks and test signals: risks are UAPI drift or include-order breakage. Test FunctionFS descriptor submission, event delivery, endpoint I/O, and kernel/userspace header compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/functionfs.h -->
