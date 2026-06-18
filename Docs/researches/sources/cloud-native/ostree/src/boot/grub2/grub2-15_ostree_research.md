# sources/cloud-native/ostree/src/boot/grub2/grub2-15_ostree

Purpose: This GRUB2 mkconfig helper delegates generation of OSTree boot menu entries to `ostree admin instutil grub2-generate` when a non-BLS GRUB configuration needs OSTree entries.

Important APIs, types, and functions: It checks for the `ostree` command, `/ostree/repo`, `/etc/default/grub`, and BLS support via `/boot/grub2/.grub2-blscfg-supported` plus `GRUB_ENABLE_BLSCFG`. It requires `GRUB_DEVICE`, sources `/usr/share/grub/grub-mkconfig_lib`, computes `DEVICE`, exports `GRUB2_BOOT_DEVICE_ID` from `grub_get_device_id`, exports `GRUB2_PREPARE_ROOT_CACHE` from `prepare_grub_to_access_device`, then execs `ostree admin instutil grub2-generate`.

Control flow: The script exits 0 for systems where it is irrelevant, exits 1 if invoked outside `grub2-mkconfig`, and otherwise runs with `set -e` before replacing itself with the OSTree generator.

State and persistence behavior: It writes no files itself. It passes computed GRUB device access state through environment variables to the generator that emits menu entries.

Dependencies and integration points: Depends on GRUB mkconfig environment, `/etc/default/grub`, GRUB helper library, OSTree system repo, and `ostree admin instutil`. It intentionally avoids generating entries when BLS can handle them.

Risks: Environment assumptions are fragile: missing `GRUB_DEVICE`, unavailable helper functions, or unexpected boot device detection can break menu generation. BLS detection must stay aligned with distro GRUB packaging.

Test signals: No direct tests in this subset. Integration is validated by grub2-mkconfig runs and bootloader entry generation tests elsewhere.
