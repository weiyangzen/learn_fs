# sources/distributed-fs/ceph-client/arch/arm/boot/dts/moxa/Makefile

Purpose: minimal Kbuild manifest for Moxa/MOXART ARM device trees. It builds `moxart-uc7112lx.dtb` when `CONFIG_ARCH_MOXART` is enabled.

Important APIs/types/functions: only `dtb-$(CONFIG_ARCH_MOXART) += moxart-uc7112lx.dtb` is exported to Kbuild. There are no overlay flags, subdirectories, or helper variables.

Control flow: Kbuild conditionally expands the DTB target list based on the architecture config.

State and persistence: no runtime state. The persistent result is the compiled UC-7112-LX DTB in the build output.

Dependencies and integration: depends on the top-level ARM DTS Kbuild including this directory, the `CONFIG_ARCH_MOXART` Kconfig symbol, and the matching `moxart-uc7112lx.dts` source.

Risks: a rename mismatch or missing target prevents the only MOXART board DTB in this directory from being built. Test with `make ARCH=arm dtbs` under a MOXART-enabled configuration or a targeted DTB build.
