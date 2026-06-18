# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_debugfs.c

## Purpose
`bfad_debugfs.c` exposes optional debugfs files under `bfa/pci_dev:<pci_name>` for driver trace, firmware trace, saved firmware trace, register reads, and register writes.

## Important APIs, Types, and Functions
`struct bfad_debug_info` carries an output buffer, inode private pointer, and buffer length. Open handlers prepare trace buffers (`bfad_debugfs_open_drvtrc`, `_fwtrc`, `_fwsave`) or register context (`bfad_debugfs_open_reg`). `bfad_debugfs_read` and `bfad_debugfs_lseek` serve trace data. `bfad_debugfs_write_regrd` parses `addr:len`, validates register range through `bfad_reg_offset_check`, reads BAR0 registers into `bfad->regdata`, and `bfad_debugfs_read_regrd` returns/free that buffer. `bfad_debugfs_write_regwr` parses `addr:val` and writes one BAR0 word. `bfad_debugfs_init` and `bfad_debugfs_exit` create/remove the root, per-port directory, and five files.

## Control Flow
When enabled by `bfa_debugfs_enable`, port initialization creates the root and per-PCI directory. Reads of `drvtrc` directly expose the in-memory `bfad->trcmod`; reads of `fwtrc`/`fwsave` allocate a vmalloc buffer and ask the IOC debug helpers to fill it under `bfad_lock`. Register read is two-step: write request string to `regrd`, then read the binary register data. Register write is immediate after parsing and range checking. Exit removes each file, the per-port directory, and the root when the atomic port count reaches zero.

## State and Persistence
State is transient except register writes, which mutate device registers directly. `bfad->regdata` and `bfad->reglen` store one pending register-read result per adapter. Trace buffers are snapshots or direct views of runtime trace state. The debugfs root lifetime is shared by all ports through `bfa_debugfs_port_count`.

## Dependencies and Integration Points
The file depends on Linux debugfs, BAR accessors from the BFA IOC layer, BFAD core state, trace modules, and `bfa_ioc_debug_fwtrc/fwsave`. It is called from the BFAD port lifecycle via prototypes in `bfad_drv.h`.

## Risks
This is a powerful diagnostic interface. `regwr` writes raw device registers and can destabilize hardware. `regrd` stores state in `bfad->regdata`, so concurrent readers/writers can race because only register accesses are locked, not all buffer lifetime transitions. `bfad_debugfs_lseek` uses `debug->buffer_len`, which is not initialized for register files opened through `bfad_debugfs_open_reg`. Permissions restrict writes to owner, but debugfs is not a stable or hardened ABI.

## Test Signals
Mount debugfs and verify file creation/removal across multiple ports and disabled mode. Exercise trace reads, invalid register parse strings, boundary offsets for CT/CB register windows, concurrent `regrd` writes/reads, and module unload with open files.
