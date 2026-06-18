# File Research: sources/block-storage/bcache-tools/show.c

`show.c` implements display functions for the main `bcache` CLI. `show_bdevs` prints a compact table of discovered bcache devices; `show_bdevs_detail` adds UUIDs, cset UUIDs, type, state, backing name, attached device, and attach cset. Both rely on `list_bdevs`.

`detail_single` decodes one device through `detail_dev` and prints fields similar to `bcache-super-show`, including backing cache mode/state or cache layout/replacement information. For cache devices it also prints feature sets through `features.c`.
