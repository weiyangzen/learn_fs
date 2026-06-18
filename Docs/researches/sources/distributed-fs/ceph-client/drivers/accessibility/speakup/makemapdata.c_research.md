# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/makemapdata.c

## Purpose
Host-side build generator that scans kernel input-key defines and Speakup private key constants, then prints a `struct st_key_init init_key_data[]` initializer.

## Important APIs, Types, And Functions
`get_define()` extracts `#define` name/value pairs from the current `infile`. `main()` seeds shift pseudo-keys, opens input headers and `spk_priv_keyinfo.h`, inserts recognized symbols with helpers from `utils.h`, and emits the table plus sentinel.

## Control Flow
`TOPDIR` and `SPKDIR` select source roots. The program scans each file, filters key names, parses numeric/hex/`KEY + offset` forms, fills the hash table, and prints every populated bucket.

## State And Persistence Behavior
Uses process-local globals from `utils.h` such as `key_table`, `def_name`, `def_val`, `infile`, and `lc`. It persists only by stdout redirection in the build.

## Dependencies, Integration Points, Risks, And Test Signals
Depends on simple C library parsing and kernel source layout. Risks are skipped complex macros and hash-bucket output order. Test default and overridden roots, known key presence, malformed defines, duplicate symbols, and final sentinel output.
