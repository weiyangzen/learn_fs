
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_module.h

## Purpose

`xe_module.h` defines the module parameter structure shared by the Xe driver and declares the global instance populated from module parameters.

## Important APIs, Types, and Functions

- `struct xe_modparam`: fields for execlist forcing, display probing, VRAM BAR sizing, GuC logging, firmware override paths, force-probe, SR-IOV VF limit, wedged mode, and SVM notifier size.
- `extern struct xe_modparam xe_modparam`.

## Control Flow

Other Xe modules read `xe_modparam` during probe and subsystem initialization to choose feature policy and firmware behavior.

## State and Persistence Behavior

`xe_modparam` is process-wide module state and remains stable after module parameter parsing, except for writable parameters exposed with write permissions.

## Dependencies and Integration Points

The header is included by PCI probing, configfs, firmware loading, and other policy-sensitive code.

## Risks and Edge Cases

The structure is a broad shared configuration object; adding fields or changing semantics affects many subsystems. Conditional `max_vfs` changes layout under `CONFIG_PCI_IOV`.

## Test Signals

Build matrix coverage with and without PCI IOV, plus module parameter parse/probe tests, should catch most regressions.
