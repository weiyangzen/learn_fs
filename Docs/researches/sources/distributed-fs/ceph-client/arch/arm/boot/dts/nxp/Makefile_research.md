# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/Makefile

Purpose: parent Kbuild manifest for NXP ARM device-tree subdirectories. It does not build DTBs directly; it delegates traversal to SoC-family folders.

Important APIs/types/functions: uses `subdir-y += imx`, `lpc`, `ls`, `mxs`, and `vf`. These Kbuild entries cause the ARM DTS build to descend into the NXP family directories.

Control flow: Make's directory traversal is the only control path. The child Makefiles then decide their own DTB targets from SoC configs.

State and persistence: no runtime state and no direct build artifacts. Persistent outputs are produced by child directories.

Dependencies and integration: depends on the parent ARM DTS build including `nxp/`, and on child directories having valid Makefiles. It is the integration junction for NXP i.MX, LPC, Layerscape, MXS, and Vybrid device trees.

Risks: removing or misspelling a `subdir-y` entry cuts an entire family out of `make dtbs`. Adding a new family requires both the directory and this traversal entry. Test signal is `make ARCH=arm dtbs` plus inspection that expected child-family DTBs appear in the build target graph.
