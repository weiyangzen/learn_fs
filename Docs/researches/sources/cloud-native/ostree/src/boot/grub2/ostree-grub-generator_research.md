# sources/cloud-native/ostree/src/boot/grub2/ostree-grub-generator

Purpose: This shell script is OSTree's built-in GRUB configuration generator for systems that do not use `grub2-mkconfig`. It converts Boot Loader Specification entry files into GRUB `menuentry` blocks.

Important APIs, types, and functions: It defines `read_config`, `populate_menu`, `populate_warning`, `populate_header`, and `generate_grub2_cfg`. Inputs are the output config path argument, the neighboring `entries` directory, optional `OSTREE_BOOT_PARTITION`, `/boot/ostree`, and `/ostree/repo`. It parses BLS records `title`, `initrd`, `linux`, `devicetree`, and `options`.

Control flow: `generate_grub2_cfg` writes a warning, a static serial/default/timeout header, then menu entries. `populate_menu` chooses a boot prefix: `/boot` when `/boot/ostree` and `/ostree/repo` are on the same device and `OSTREE_BOOT_PARTITION` is unset, otherwise the environment-provided boot partition prefix. It iterates entry configs with `ls -v -r`, reads each config, and appends GRUB stanza text.

State and persistence behavior: Appends to the new grub config path supplied by the caller, which is intended to be an atomically safe temporary target during bootloader updates. It reads BLS entry files but does not mutate them.

Dependencies and integration points: Invoked by `ostree-bootloader-grub2.c`, relies on POSIX/busybox-compatible shell behavior, `stat`, `ls -v -r`, BLS entry format, and GRUB syntax.

Risks: Unquoted variable use and simple line parsing can be sensitive to spaces or shell metacharacters in paths/titles/options. The script appends rather than truncates, so the caller must provide a fresh output file. Embedded systems with minimal tools must provide compatible `stat` and `ls`.

Test signals: No direct tests here. Generated grub.cfg inspection and boot tests are the main validation signals.
