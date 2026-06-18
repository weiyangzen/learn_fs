# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/console.h

This header declares SRM console callback interfaces and console initialization helpers. It includes UAPI console constants and exposes callback functions for puts/getc/open/close/read/getenv/setenv/save-env, plus `srm_fixup`, `srm_puts`, `srm_printk`, `callback_init_done`, and `callback_init`.

The APIs are firmware integration points used by boot code and early kernel console paths. They operate on SRM units, channels, environment ids, and HWRPB/CRB callback data. State is external firmware callback state plus `callback_init_done`.

Risks include callback calling conventions, buffer lengths, HWRPB callback relocation through `srm_fixup`, and using console callbacks after boot code has started moving or overwriting its image. Test signals are SRM boot logs, environment variable reads, and early printk behavior.
