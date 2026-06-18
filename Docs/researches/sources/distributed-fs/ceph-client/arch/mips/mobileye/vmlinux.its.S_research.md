<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/vmlinux.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/mobileye/vmlinux.its.S

### Purpose
`vmlinux.its.S` is a generic preprocessed FIT image source for a MIPS Linux kernel image.

### Important APIs, Types, And Functions
It defines root `description`, address-cell width, an `images/kernel` node with incbin `VMLINUX_BINARY`, type `kernel`, arch `mips`, compression `VMLINUX_COMPRESSION`, load and entry addresses, and SHA1 hash. It also defines a default configuration pointing to `kernel`.

### Control Flow
Build rules preprocess macros such as `KERNEL_NAME`, `ADDR_CELLS`, `ADDR_BITS`, `VMLINUX_BINARY`, `VMLINUX_LOAD_ADDRESS`, and `VMLINUX_ENTRY_ADDRESS`, then pass the ITS to FIT tooling.

### State, Persistence, And Dependencies
Persistent output is a FIT image containing the kernel. Dependencies include build-defined macros, the compressed or raw vmlinux binary, and `mkimage` or equivalent FIT processing.

### Integration Points
Board fragments such as `board-epm5.its.S` can extend the `images` and `configurations` nodes to add FDTs and board-specific configs.

### Risks
Incorrect load or entry address macros produce unbootable FIT images. Compression metadata must match the binary contents. SHA1 is a compatibility hash, not a strong security boundary.

### Test Signals
Build FIT images for supported address widths and compression modes, inspect resulting ITS/FIT metadata, and boot the default configuration plus board-extended configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mobileye/vmlinux.its.S -->
