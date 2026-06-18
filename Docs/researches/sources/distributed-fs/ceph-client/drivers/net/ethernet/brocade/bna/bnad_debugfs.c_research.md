# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bnad_debugfs.c

## Purpose
Implements optional debugfs support for the BNA driver. It creates `/sys/kernel/debug/bna/pci_dev:<pci_name>/` entries for firmware trace capture, saved firmware crash trace capture, raw register reads and writes, and aggregate driver/IOC/CEE/flash information.

## Important APIs, Types, and Functions
`struct bnad_debug_info` stores per-open debug buffers and private BNA pointers. Open/read/write handlers include `bnad_debugfs_open_fwtrc`, `bnad_debugfs_open_fwsave`, `bnad_debugfs_open_reg`, `bnad_debugfs_open_drvinfo`, `bnad_debugfs_read`, `bnad_debugfs_read_regrd`, `bnad_debugfs_write_regrd`, and `bnad_debugfs_write_regwr`. Utility functions include `bnad_get_debug_drvinfo`, `bnad_debugfs_lseek`, `bnad_debugfs_release`, `bnad_debugfs_buffer_release`, and register-bound validation `bna_reg_offset_check`. Public entry points are `bnad_debugfs_init` and `bnad_debugfs_uninit`.

## Control Flow and State
Initialization lazily creates the global `bna` root and a per-port directory named `pci_dev:<pci_name>`, then installs files `fwtrc`, `fwsave`, `regrd`, `regwr`, and `drvinfo`. Firmware trace opens allocate a fixed trace buffer and fill it through `bfa_nw_ioc_debug_fwtrc()` or `bfa_nw_ioc_debug_fwsave()` under `bna_lock`. Driver-info opens allocate `struct bnad_drvinfo`, collect IOC attributes synchronously under lock, then issue CEE and flash attribute commands and wait for completions under `conf_mutex`.

Register reads are two-step: writing `addr:len` to `regrd` validates the masked BAR0 offset and length, allocates `bnad->regdata`, reads dwords under `bna_lock`, and later `read()` drains and frees that buffer. Register writes parse `addr:val`, validate one dword, and write BAR0 under `bna_lock`.

## State and Persistence Behavior
Debug buffers are per-open except register read data, which is stored in `bnad->regdata`/`reglen` until fully read or replaced. The global root dentry and atomic port count persist across adapters. Register writes directly mutate device MMIO state and are intentionally persistent until hardware or firmware changes it.

## Dependencies and Integration Points
Depends on Linux debugfs, module ownership, BAR0 access through `bfa_ioc_bar0`, BFA IOC debug helpers, CEE and flash APIs, BNAD completions, and BNAD locks. It is enabled from `bnad_pci_probe()` through the `bna_debugfs_enable` module parameter and cleaned up from probe failure/remove paths.

## Risks and Test Signals
Risk is high for `regwr`: it exposes raw MMIO writes to privileged debugfs users and can destabilize hardware. Other risks include `bnad->regdata` being shared per adapter across concurrent readers/writers, offset/length overflow mistakes, waiting for firmware completions while the device is resetting, and debugfs root lifetime with multiple ports. Test signals include debugfs mount with multiple adapters, concurrent `regrd` readers, invalid offset/length inputs, firmware trace after firmware failure, and remove while files are open.
