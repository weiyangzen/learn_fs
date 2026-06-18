# sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_dev.h

Purpose: declares the HMC drive misc-device lifecycle interface.

Important APIs/types/functions: `hmcdrv_dev_init()` creates `/dev/hmcdrv`; `hmcdrv_dev_exit()` removes it.

Control flow: no standalone flow. Module init/exit code calls these functions.

State and persistence behavior: no state in the header.

Dependencies and integration points: consumed by the HMC driver module core; implementation depends on miscdevice.

Risks and test signals: compile/link coverage ensures module core and device implementation remain aligned.
