# File Research: sources/block-storage/bcache-tools/bcache-export-cached

This shell helper is designed for udev `IMPORT{program}` on a `/dev/bcacheN` cached device. It walks `/sys/class/block/$DEVNAME/slaves/*`, runs `bcache-super-show` on each slave device, and extracts `sb.version`, `dev.uuid`, and non-empty `dev.label` with awk.

It emits `CACHED_UUID=<uuid>` and optional `CACHED_LABEL=<label>` only for backing-device superblock versions `1`, `4`, or `6`. The rule file then uses those values to create stable `bcache/by-uuid` and `bcache/by-label` symlinks.
