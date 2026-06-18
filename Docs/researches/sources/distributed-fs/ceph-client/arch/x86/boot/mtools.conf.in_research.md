# sources/distributed-fs/ceph-client/arch/x86/boot/mtools.conf.in

Purpose: template mtools configuration for x86 boot image generation.

Important APIs and state: defines drives `a:`, `v:`, `w:`, `h:`, and `p:` mapping to floppy device, 1.44 MB image, 2.88 MB image, and hard-disk image/partition using `@OBJ@` substitution.

Control flow: none; consumed by mtools commands run from `genimage.sh`.

Dependencies and integration: generated into a concrete config file by the build system and exported as `MTOOLSRC`.

Risks and test signals: wrong object directory substitution or geometry breaks image creation. Test `make fdimage144`, `fdimage288`, and `hdimage` targets using the generated config.
