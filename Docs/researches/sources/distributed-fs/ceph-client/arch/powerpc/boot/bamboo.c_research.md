# sources/distributed-fs/ceph-client/arch/powerpc/boot/bamboo.c

## Purpose
Native Bamboo 440EP boot-wrapper board initialization and FDT fixups.

## Important APIs, Types, And Control Flow
`bamboo_init(void *mac0, void *mac1)` stores firmware MAC-address pointers, sets `platform_ops.fixups` to `bamboo_fixups`, sets `platform_ops.exit` to `ibm44x_dbcr_reset`, initializes the FDT with `_dtb_start`, and initializes serial console. `bamboo_fixups()` applies fixed clock inputs, SDRAM memory sizing, EMAC/MAL quiesce, and MAC-address properties for `ethernet0` and `ethernet1`.

## State, Dependencies, Risks, And Tests
Persistent boot-wrapper state is the cached MAC pointers and `platform_ops` callbacks; external state is FDT mutation and hardware quiesce. Dependencies include `4xx.c`, `44x.h`, DCR helpers, and device-tree ops. Risks include hard-coded clock values, invalid MAC pointers copied from firmware board info, and reset/quiesce behavior on firmware variants. Test with Bamboo cu/tree images, FDT clock/memory/MAC property inspection, and reboot path through DBCR reset.
