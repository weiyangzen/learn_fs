# sources/distributed-fs/ceph-client/drivers/char/Kconfig

## Purpose
This Kconfig file defines the character-device driver menu and includes several char-related submenus. In this work item, its relevant additions are the SPARC64 ADI driver option and unconditional AGP submenu inclusion through the Makefile.

## Important APIs, Types, and Functions
It declares many config symbols including `TTY_PRINTK`, `PRINTER`, `PPDEV`, `VIRTIO_CONSOLE`, `/dev/mem` and `/dev/port` options, HPET, hardware-specific char drivers, and `ADI`. `ADI` is a tristate "SPARC Privileged ADI driver" depending on `SPARC64` and defaulting to module.

## Control Flow
During configuration, this menu sources TTY, IPMI, hardware random, TPM, s390 char, and xillybus Kconfigs. Selecting symbols controls object inclusion in `drivers/char/Makefile`.

## State and Persistence Behavior
The file only affects `.config`. Runtime state is in the selected drivers. `ADI` selection results in a privileged miscdevice for reading/writing SPARC ADI memory tags.

## Dependencies and Integration Points
It integrates architecture-specific drivers with generic char-device infrastructure. The `ADI` option depends on SPARC64 architecture support functions such as `adi_capable()` and `adi_blksize()`.

## Risks
Many options expose low-level hardware or physical memory interfaces; misconfiguration can expand user-space attack surface. The `ADI` help explicitly targets privileged consumers such as crash tooling, so permissions and architecture availability matter.

## Test Signals
Kconfig coverage should confirm architecture dependencies, module names, and that selected symbols produce expected Makefile objects. For `ADI`, verify it is offered only on SPARC64.
