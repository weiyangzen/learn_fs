<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/uvesafb.h -->
# sources/distributed-fs/ceph-client/include/uapi/video/uvesafb.h

Purpose: defines UAPI structs and flags for uvesafb userspace VBE helper tasks, virtual 8086 register state, and VBE information block layout.

Important APIs and types: `v86_regs` carries x86 register state for BIOS calls. Task flags `TF_VBEIB`, `TF_BUF_ESDI`, `TF_BUF_ESBX`, `TF_BUF_RET`, and `TF_EXIT` describe buffer and exit behavior. `uvesafb_task` carries flags, buffer length, and registers. `vbe_ib` is a packed VBE Info Block with signature, version, OEM pointers, capabilities, mode list, memory, reserved/OEM/misc data.

Control flow: the kernel framebuffer driver delegates VBE BIOS operations to a userspace helper, which receives a task, executes or emulates the BIOS call, and returns registers and optional buffers.

State and persistence: no kernel state is stored here. Task contents are transient; `vbe_ib` is display adapter firmware-provided capability data.

Dependencies and integration points: depends on Linux types and integrates with uvesafb, v86d-style helpers, x86 VBE BIOS conventions, and framebuffer mode selection.

Risks and test signals: risks include packed layout compatibility, pointer-like VBE far pointer fields in 32-bit values, buffer length validation, and helper/kernel protocol mismatch. Test helper round trips, VBE info parsing, mode list buffers, invalid flags, and non-x86 build isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/uvesafb.h -->
