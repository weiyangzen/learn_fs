# sources/distributed-fs/ceph-client/sound/soc/sti/Makefile

Purpose: builds the STi ASoC support as one composite object.

Important entries: `snd-soc-sti-y := sti_uniperif.o uniperif_player.o uniperif_reader.o` and `obj-$(CONFIG_SND_SOC_STI) += snd-soc-sti.o`.

Control flow and integration: when `SND_SOC_STI` is enabled, common probe code, player code, and reader code are linked into one module/object, allowing internal shared symbols and exported init helpers to resolve together.

State and persistence: no runtime state; build grouping determines module lifetime for all STi uniperipheral DAIs.

Dependencies: sibling Kconfig, common Linux kbuild composite-object conventions, and top-level ASoC build traversal.

Risks: all player and reader code is included even for systems using only one direction. Future split modules would need symbol export and init ordering review.

Test signals: module build confirms `snd-soc-sti.o` contains all three translation units; boot with each compatible string to ensure shared module autoload covers all variants.
