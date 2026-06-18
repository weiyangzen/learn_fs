# sources/distributed-fs/ceph-client/arch/m68k/emu/Makefile

Purpose: kbuild manifest for m68k emulator/NatFeat support.

Important entries: `obj-y += natfeat.o` always builds base Native Features support for this directory, while `obj-$(CONFIG_NFBLOCK)`, `obj-$(CONFIG_NFCON)`, and `obj-$(CONFIG_NFETH)` conditionally build block, console, and Ethernet NatFeat drivers.

Control flow and state: kbuild uses these object lists to select compiled objects; no runtime state exists. The file defines integration boundaries for the ARAnyM emulator support stack.

Dependencies and integration: Linux kbuild, m68k architecture config symbols, and the source files in the same folder. `natfeat.o` must be present for optional drivers because they call `nf_get_id()`/`nf_call()`.

Risks and test signals: building optional drivers without base NatFeat support would fail, but unconditional `natfeat.o` prevents that. Test by building configs with each `CONFIG_NF*` option enabled/disabled and checking link inclusion.
