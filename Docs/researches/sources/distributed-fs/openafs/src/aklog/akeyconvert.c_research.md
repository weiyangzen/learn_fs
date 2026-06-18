# sources/distributed-fs/openafs/src/aklog/akeyconvert.c

## Purpose

`akeyconvert.c` implements the `akeyconvert` administrative migration tool for OpenAFS upgrades using the rxkad-k5 extension. It reads keys from the server `rxkad.keytab`, detects key identifier conflicts that cannot be represented in `KeyFileExt`, and writes compatible non-DES keys into `KeyFileExt`. By default it writes only the newest kvno for each principal; the `-all` flag writes older keys as well.

## Important APIs, types, and functions

The file uses Kerberos keytab APIs, OpenAFS server configuration APIs, typed-key APIs, and the OpenAFS `cmd` parser. Portability macros abstract Kerberos keytab entry fields: `deref_entry_keylen`, `deref_entry_keyval`, and `deref_entry_enctype` handle `key` versus `keyblock` layouts. Compatibility macros also normalize `krb5_free_keytab_entry_contents` and `krb5_free_unparsed_name`.

`ktent_to_typedKey` converts a `krb5_keytab_entry` to `struct afsconf_typedKey`. DES enctypes 1, 2, and 3 map to `afsconf_rxkad` with subtype zero; other enctypes map to `afsconf_rxkad_krb5` with the Kerberos enctype. `princ_sort`, `kvno_sort`, `etype_sort`, `ke_sort`, and `full_sort` define ordering. `slurp_keytab` reads the whole keytab into memory. `check_dups` rejects duplicate kvno/enctype pairs. `convert_kt` writes selected entries into `KeyFileExt` with `afsconf_AddTypedKey`. `free_ents` releases keytab-entry contents and the entry array. `CommandProc` is the command handler, and `main` registers the optional `-all` flag.

## Control flow

`main` creates a command syntax with the description "Convert cell keys for the 1.6->1.8 OpenAFS upgrade", adds `-all`, dispatches, and returns boolean failure. `CommandProc` initializes a Kerberos context, opens the server configuration directory `AFSDIR_SERVER_ETC_DIR`, builds the keytab path from `dir->name` and `AFSDIR_RXKAD_KEYTAB_FILE`, and calls `slurp_keytab`.

`slurp_keytab` resolves the keytab, performs a first sequential scan to count entries, allocates an array, then performs a second scan to copy entries into that array. If the keytab changes between passes and more entries are seen than allocated, it warns and stops early. After reading, `CommandProc` sorts by kvno/enctype using `ke_sort` and calls `check_dups` so duplicates across principals are fatal before any writes. It then sorts by principal, descending kvno, and descending enctype using `full_sort`.

`convert_kt` walks the fully sorted array. For each principal, it tracks the first kvno as the newest because the sort places higher kvnos first. Without `-all`, entries for older kvnos of the same principal are skipped. Each remaining key is converted to an OpenAFS typed key. Single-DES rxkad keys are explicitly not added to `KeyFileExt`; the tool prints a warning and continues. Duplicate existing KeyFileExt entries (`AFSCONF_KEYINUSE`) also produce a warning and continue. Other conversion or write errors abort the command.

## State and persistence behavior

The only intended persistent mutation is adding typed keys to the server configuration directory's `KeyFileExt` through `afsconf_AddTypedKey`. Input state is the existing `rxkad.keytab` under the same server config directory. The program keeps all keytab entries in memory until conversion completes, then frees entries, path strings, Kerberos context, and the AFS config directory handle. It prints diagnostics to stderr and a final count to stdout.

## Dependencies and integration points

This file depends on Kerberos keytab/principal APIs, com_err headers selected by configure checks, OpenAFS `afsconf` directory and typed-key APIs, server path constants from `afs/dirpath.h`, key constants from `afs/keys.h`, and `roken` for portability functions such as `asprintf`. It integrates with the `aklog` build through `Makefile.in`, which links it with auth, cmd, opr, Kerberos, hcrypto, roken, and pthread-related libraries.

## Risks and edge cases

`princ_sort` initializes and frees a Kerberos context on every comparison, which can be expensive for large keytabs and uses `opr_Verify` assertions for operations that can theoretically fail. The qsort comparators depend on Kerberos principal unparsing for deterministic ordering when principals differ. `check_dups` only checks adjacent entries after sorting by kvno/enctype; that is correct for duplicates but should be covered by tests. The first pass in `slurp_keytab` counts entries, and a concurrent keytab shrink/growth can make `*nents` differ from the number actually filled; the code warns only when more entries appear than allocated. `convert_kt` parses a well-known anonymous principal as the initial sentinel and frees it at exit; if `krb5_parse_name` fails before initialization, cleanup must still tolerate that path. Error reporting after `convert_kt` says "errno" even though many returned codes are OpenAFS/Kerberos codes rather than `errno`.

## Test signals

Useful tests include keytabs with one principal and multiple kvnos, multiple principals with overlapping kvno/enctype pairs, duplicate kvno/enctype pairs across principals, DES-only keys, mixed DES and rxkad-k5 keys, existing KeyFileExt entries, empty keytabs, unreadable keytabs, and `-all` versus default selection. Build tests should cover Kerberos implementations exposing `key` versus `keyblock` keytab entry fields and different com_err include paths. Runtime tests should verify that duplicate identifiers cause no writes, existing keys are skipped without aborting, and successful writes can be read back from `KeyFileExt`.
