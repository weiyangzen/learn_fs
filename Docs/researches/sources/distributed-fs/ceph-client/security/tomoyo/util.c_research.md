# sources/distributed-fs/ceph-client/security/tomoyo/util.c

## Purpose

This file contains TOMOYO's shared utility layer for policy parsing, path/domain validation, pattern matching, request initialization, mode lookup, time conversion, executable lookup, and learning-mode quota enforcement.

## Important APIs, types, and functions

Important exported helpers include `tomoyo_convert_time`, `tomoyo_permstr`, `tomoyo_read_token`, `tomoyo_get_domainname`, `tomoyo_parse_ulong`, `tomoyo_print_ulong`, `tomoyo_parse_name_union`, `tomoyo_parse_number_union`, `tomoyo_str_starts`, `tomoyo_normalize_line`, `tomoyo_correct_word`, `tomoyo_correct_path`, `tomoyo_correct_domain`, `tomoyo_domain_def`, `tomoyo_find_domain`, `tomoyo_fill_path_info`, `tomoyo_path_matches_pattern`, `tomoyo_get_exe`, `tomoyo_get_mode`, `tomoyo_init_request_info`, and `tomoyo_domain_quota_is_ok`. Global state includes `tomoyo_policy_lock`, `tomoyo_policy_loaded`, and `tomoyo_index2category`.

## Control Flow

Parsing helpers destructively tokenize policy lines, parse decimal/octal/hex values and ranges, and resolve `@` group references. Validation walks TOMOYO escape syntax, path requirements, domain names, recursion patterns, and character classes. Pattern matching first compares constant prefixes, then recursively handles component patterns, subtraction `\-`, repetition `\{...\}`, wildcards, byte escapes, and digit/hex/alpha classes. Request initialization chooses the active domain and computes mode from profile, category defaults, and global default. Quota checking counts effective ACL permission bits while tolerating races, then logs and flags the domain when learning-mode quota is exceeded.

## State and Persistence

`tomoyo_policy_lock` serializes policy mutations. `tomoyo_policy_loaded` gates enforcement modes so policy is disabled before load. Parsed path info stores hash, constant prefix length, directory flag, and patterned flag in caller-provided objects. Quota warnings persist in domain flags to avoid repeated learning-mode logs.

## Dependencies and Integration Points

It depends on TOMOYO domain, profile, group, ACL, logging, and path intern tables; on kernel hashing, time conversion, executable lookup, and character helpers; and on SRCU policy traversal. Most TOMOYO parsers and checkers depend on these utilities.

## Risks and Test Signals

Risks include parser mutation surprises, escape grammar drift, recursive pattern backtracking cost, race-tolerant quota counts, mode defaults masking policy expectations, and group reference lifetime handling. Tests should cover every escape form, invalid words/domains, numeric bases/ranges, pattern subtraction and repetition, directory-vs-file matching, profile inheritance, learning quota warnings, and current executable path lookup.
