# sources/distributed-fs/openafs/src/bozo/bos_util.c

`bos_util.c` is a local server-side key-management utility for manipulating OpenAFS server keys without going through bosserver RPCs. It supports `add`, `adddes`, optionally `srvtab2keyfile`, `delete`, and `list`.

The primary API is `main`, which opens `AFSDIR_SERVER_ETC_DIR`, parses argv manually, prompts for passphrases with `UI_UTIL_read_pw_string`, converts them using `ka_StringToKey` or `DES_string_to_key`, and calls `afsconf_AddKey`, `afsconf_DeleteKey`, or `afsconf_GetKeys`. The list path prints raw key bytes in printable and octal forms.

Control flow is a straight opcode switch over `argv[1]`; all errors print to stdout/stderr and exit nonzero. State is persistent in the server configuration directory key files, with no network/Rx involvement. Dependencies are afsconf, hcrypto UI/DES, kauth utilities, and legacy Kerberos support when compiled.

Risks include direct display of secret key material in `list`, legacy DES handling, minimal input validation around numeric kvnos, and hard process exits that make it unsuitable as a library. Test signals are command-level: add/delete/list against a temporary afsconf dir, password mismatch behavior, and compile coverage for `KERBEROS` conditionals.
