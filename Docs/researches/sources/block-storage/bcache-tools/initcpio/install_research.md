# File Research: sources/block-storage/bcache-tools/initcpio/install

This mkinitcpio install hook adds the `bcache` kernel module, udev helper binaries `bcache-export-cached`, `bcache-register`, and `probe-bcache`, plus the `69-bcache.rules` file. Its help text states that the hook auto-assembles bcache devices and requires the udev hook.
