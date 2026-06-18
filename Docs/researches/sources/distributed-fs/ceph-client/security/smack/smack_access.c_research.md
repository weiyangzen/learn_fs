# sources/distributed-fs/ceph-client/security/smack/smack_access.c

## Purpose
`smack_access.c` implements Smack label repository management, core rule lookup and access decisions, audit logging, label parsing/import, NetLabel secattr population, secid-to-label translation, and MAC override privilege checks.

## Important APIs, Types, and Functions
It defines special labels `?`, `^`, `*`, `_`, and `@`, the global `smack_known_list`, `smack_known_hash`, `smack_known_lock`, `smack_onlycap_list`, and `smack_onlycap_lock`. Public functions include `smk_access_entry()`, `smk_access()`, `smk_tskacc()`, `smk_curacc()`, `smack_str_from_perm()`, `smack_log()`, `smk_insert_entry()`, `smk_find_entry()`, `smk_parse_label_len()`, `smk_parse_smack()`, `smk_netlbl_mls()`, `smack_populate_secattr()`, `smk_import_entry()`, `smk_import_valid_label()`, `smack_from_secid()`, `smack_privileged_cred()`, and `smack_privileged()`.

## Control Flow
`smk_access()` first applies hardcoded Smack rules: star subject denied, web subject/object allowed, star object allowed, equal labels allowed, hat/floor read-or-lock allowances. Otherwise it RCU-searches the subject label's rule list with `smk_access_entry()` and checks requested bits against allowed bits, with write implying lock. Task/current access wrappers add task-local restrictions and `CAP_MAC_OVERRIDE` onlycap handling. Label import parses a valid leading label, locks the global repository, reuses an existing entry or allocates/populates a new `smack_known`, assigns a secid, initializes rules, and publishes via RCU list/hash insertion.

## State and Persistence
Known labels are permanent in-memory objects and are shared by pointer. Secids monotonically increase from above the built-in labels. NetLabel attributes are cached inside each label. onlycap state restricts which labels may use MAC override capability.

## Dependencies and Integration Points
The file depends on Linux capability checks, RCU lists, NetLabel category maps/cache, audit, task creds, and constants from `smack.h`. LSM hooks call these helpers for file, task, IPC, network, and policy-interface decisions.

## Risks
Pointer/string identity assumptions require labels to come from the known-label repository. Label parsing must reject separators and options safely. Permanent label allocation can grow without deletion. Audit behavior differs under bringup mode. onlycap checks combine capability state with label membership and can affect administrative recovery.

## Test Signals
Tests should cover all built-in label shortcuts, explicit rule grants/denials, write-implies-lock, task-local restriction, `CAP_MAC_OVERRIDE` with empty and populated onlycap lists, invalid label strings, duplicate label imports, secid lookup misses, NetLabel direct versus mapped labeling, and audit logging filters.
