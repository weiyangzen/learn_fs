<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/bioscalls.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/bioscalls.c

Purpose: Low-level x86 protected-mode thunk layer for invoking legacy PnP BIOS functions and wrapping those functions in C helpers.

Important APIs/types/functions: `pnp_bios_callfunc` assembly performs a 16-bit far call and return. `call_pnp_bios()` sets GDT descriptors, serializes calls with `pnp_bios_lock`, disables IRQs, tracks fault recovery globals, and returns firmware status. Wrappers cover node info, get/set device node, docking info, static resources, ISA config, ESCD info/read. `pnpbios_calls_init()` initializes callpoint and GDT descriptor bases.

Control flow: public wrappers check `pnp_bios_present()`, call the firmware function number through `call_pnp_bios()`, translate/print status on error, and sometimes update returned node numbers. `set_dev_node()` optionally refreshes the node after setting current config.

State/persistence: global callpoint, per-CPU GDT descriptors, fault flags, and firmware NVRAM/current configuration. `pnp_bios_is_utter_crap` disables further calls after fatal BIOS behavior.

Dependencies/integration: x86_32 segmentation/GDT internals, PnP BIOS install structure from `core.c`, packed PnP BIOS structs, spinlocks, SMP CPU pinning, and firmware memory mappings.

Risks: this is inherently high-risk legacy firmware execution outside normal kernel segments. Incorrect descriptor setup or BIOS faults can destabilize the system. Several calls pass 64 KiB buffers and trust firmware status. IRQ-off serialized execution may still be unsafe on buggy BIOSes.

Test signals: x86_32 PnP BIOS emulator/hardware, invalid/no BIOS present paths, DMI-blacklisted systems, ESCD/node service errors, and fault flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/bioscalls.c -->
