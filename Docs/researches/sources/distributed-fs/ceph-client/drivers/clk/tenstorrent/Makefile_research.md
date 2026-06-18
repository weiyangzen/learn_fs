# sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/Makefile

## Purpose

This Makefile connects `CONFIG_TENSTORRENT_ATLANTIS_PRCM` to the Atlantis PRCM clock-controller object.

## Important APIs, Types, And Functions

The only build rule is `obj-$(CONFIG_TENSTORRENT_ATLANTIS_PRCM) += atlantis-prcm.o`.

## Control Flow

Kbuild includes `atlantis-prcm.o` as built-in, module, or omitted according to the Kconfig symbol value.

## State And Persistence Behavior

There is no runtime state. The file only affects build composition.

## Dependencies And Integration Points

It integrates with `drivers/clk/tenstorrent/Kconfig` and the top-level clock-driver build. Any future Tenstorrent clock files must be added here or they will not build.

## Risks And Edge Cases

The rule is intentionally simple. The main risk is forgetting to update it when the driver is split into multiple objects or when domain-specific files are introduced.

## Test Signals

Check that enabling `CONFIG_TENSTORRENT_ATLANTIS_PRCM=m` produces `atlantis-prcm.ko`, and enabling it built-in links the object into the kernel.
