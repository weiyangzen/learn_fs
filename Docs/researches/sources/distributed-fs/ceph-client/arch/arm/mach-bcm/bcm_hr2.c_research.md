# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_hr2.c

Purpose: provides Broadcom `bcm_hr2` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
