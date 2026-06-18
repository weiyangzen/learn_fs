# File Research: sources/block-storage/bcache-tools/debug/print_key.c

`print_key` decodes three numeric bcache btree-key words: `high`, `low`, and `ptr`. It defines bkey bitfield extractors for pointer count, header size, checksum type, pinned/dirty flags, size, inode, pointer device, pointer offset, and generation, then prints decimal and hex values.

Notable bug: parse-error checks for `low` and `ptr` mistakenly test `k.high == ULLONG_MAX` instead of the parsed field, so invalid second/third arguments may not be reported correctly.
