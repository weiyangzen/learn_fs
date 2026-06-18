# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_debugfs.c

## Purpose
`ice_debugfs.c` provides minimal debugfs directory lifecycle support for the ice driver. It creates a module-level debugfs root and per-PF subdirectories named by PCI device name, and removes them during PF teardown or module exit.

## Important APIs, Types, And Functions
The file has one static global, `ice_debugfs_root`. Public functions are `ice_debugfs_init()`, `ice_debugfs_exit()`, `ice_debugfs_pf_init()`, and `ice_debugfs_pf_deinit()`. Per-PF state is stored in `pf->ice_debugfs_pf`.

## Control Flow
Module/driver initialization calls `ice_debugfs_init()`, which creates `/sys/kernel/debug/<module-name>`. PF initialization calls `ice_debugfs_pf_init()`, which creates a child directory using `pci_name(pf->pdev)`. PF deinit removes the PF subtree recursively and nulls the pointer. Module exit removes the root recursively and clears the global pointer.

## State And Persistence
Debugfs entries are runtime-only kernel debug state. They are not persistent across module unload or reboot. The only retained state is the root dentry and per-PF dentry pointer.

## Dependencies And Integration Points
It depends on `<linux/debugfs.h>`, `ice.h`, PF PCI device state, `KBUILD_MODNAME`, and kernel debugfs APIs. Other ice debugfs files can add files below the per-PF directory after `ice_debugfs_pf_init()` succeeds.

## Risks
`debugfs_create_dir()` may return an error pointer, which this file handles for PF init and logs for root init. If root creation fails but PF init is still called, behavior depends on debugfs accepting an error/NULL parent; callers should order and gate setup carefully. Recursive removal must be paired with pointer nulling to avoid stale dentries.

## Test Signals
Probe/remove cycles with debugfs enabled, root creation failure injection if available, multiple PFs creating unique PCI-name directories, module unload cleanup, and checking that no debugfs dentries remain after PF removal are useful signals.
