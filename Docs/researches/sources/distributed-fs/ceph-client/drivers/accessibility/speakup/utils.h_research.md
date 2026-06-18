# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/utils.h

## Purpose
`utils.h` is a small userspace build-time utility header for Speakup keymap/table generation tools. It supplies global parser state, a simple name hash table, file opening/error helpers, and key insertion/lookup helpers.

## Important APIs, Types, And Functions
It defines `MAXKEYS`, `MAXKEYVAL`, `HASHSIZE`, sentinel values `is_shift`, `is_spk`, and `is_input`, plus `struct st_key { name, next, value, shift }`. Global state includes `key_table`, `extra_keys`, `def_name`, `def_val`, `infile`, `lc`, and `filename`. Inline helpers are `open_input()`, `oops()`, `hash_name()`, `find_key()`, and `add_key()`.

## Control Flow
Generation tools call `open_input()` to form a path and open the input file, increment `lc` while parsing, use `hash_name()` to normalize names to lowercase and select a bucket, then call `find_key()` or `add_key()` to resolve or register key names. Errors are fatal through `oops()`, which reports the current file and line and exits.

## State And Persistence
The hash table is process-local state in the generator. `hash_name()` mutates its input string by lowercasing it. `add_key()` stores duplicated key names with `strdup()` and monotonically consumes entries from `extra_keys`; entries are not freed because the generator is short-lived.

## Dependencies And Integration Points
The header uses libc I/O and string APIs (`stdio.h`, `fopen`, `snprintf`, `fprintf`, `exit`, `strdup`, `strcmp`, `tolower`, `isupper`). It is meant for Speakup host tools, not kernel object code.

## Risks
Because this header defines globals, including it in more than one translation unit would create multiple-definition problems. The fixed `MAXKEYS` table can abort on large maps, `filename` truncation is not checked, and `hash_name()` modifies caller-owned strings. Fatal `exit(1)` behavior is appropriate for generators but unsuitable for reusable libraries.

## Test Signals
Useful tests parse key names with different case, detect duplicate keys, exhaust or approach `MAXKEYS`, and verify error messages include filename and line count. Build tests should ensure the header is used only by intended userspace tools.
