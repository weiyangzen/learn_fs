# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan865x/Makefile

Purpose: Kbuild fragment for the LAN865x MAC-PHY driver.

Important behavior: `obj-$(CONFIG_LAN865X) += lan865x.o` compiles the single implementation file into the built-in image or module based on the Kconfig symbol.

Control flow and state: no runtime behavior. The only persistent effect is the build graph edge from `CONFIG_LAN865X` to `lan865x.o`.

Dependencies and integration points: depends on the surrounding Microchip Ethernet Makefile recursing into the `lan865x` directory and on the Kconfig symbol being visible.

Risks and test signals: the file is simple, but renaming the object or symbol breaks module generation. Test with `make M=drivers/net/ethernet/microchip/lan865x` or equivalent tree builds for modular and built-in configurations.
