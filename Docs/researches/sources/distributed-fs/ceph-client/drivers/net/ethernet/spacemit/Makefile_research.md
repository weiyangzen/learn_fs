# sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/Makefile

## Purpose
The Makefile wires the SpacemiT K1 EMAC implementation into kbuild.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_SPACEMIT_K1_EMAC) += k1_emac.o` builds the driver when the Kconfig symbol is enabled.

## Control Flow
kbuild evaluates the `CONFIG_SPACEMIT_K1_EMAC` tristate and either links `k1_emac.o` into the kernel or builds it as a module.

## State And Persistence
Build-only file; no runtime state.

## Dependencies And Integration Points
Depends on the parent networking Makefile including the `spacemit/` directory and on the Kconfig symbol declared in `spacemit/Kconfig`.

## Risks
The Makefile has a single object and no composite module list, so additional source files would require explicit edits.

## Test Signals
`make M=drivers/net/ethernet/spacemit` or a full kernel build should emit `k1_emac.o` when `CONFIG_SPACEMIT_K1_EMAC` is enabled.
