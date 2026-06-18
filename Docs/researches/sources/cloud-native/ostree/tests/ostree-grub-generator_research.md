<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/ostree-grub-generator -->
## sources/cloud-native/ostree/tests/ostree-grub-generator

Purpose: shell GRUB2 config generator used as OSTree's built-in/custom generator template for systems not using `grub2-mkconfig`.

Important APIs/functions: `read_config()` parses BootLoaderSpec fields into globals; `populate_menu()` determines `boot_prefix`, iterates loader entry `.conf` files in version-reverse order, and appends `menuentry`, `linux`, `initrd`, and optional `devicetree` lines; `populate_warning()`, `populate_header()`, and `generate_grub2_cfg()` write the final file.

Control flow/state: takes the target grub config path as argument 2, derives entries path beside it, and appends generated content. It relies on global shell variables for parsed fields and accumulated `menu`.

Dependencies/integration: called from `ostree-bootloader-grub2.c` or tests via `OSTREE_GRUB2_EXEC`. Uses portable `/bin/sh`, `basename`, `dirname`, `stat`, `ls -v -r`, `cut`, and `printf`.

Risks/test signals: unquoted expansions and `printf "$menu"` can mishandle special characters; missing `OSTREE_BOOT_PARTITION` with separate boot layouts is sensitive. Signals are cross-checker validation against loader entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/ostree-grub-generator -->
