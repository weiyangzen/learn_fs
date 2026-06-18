# sources/distributed-fs/ceph-client/security/ipe/policy_parser.c

Purpose: Parses plaintext IPE policy text into validated `struct ipe_parsed_policy` decision tables.

Important APIs/types/functions: Implements `ipe_parse_policy()` and `ipe_free_parsed_policy()`. Internals include `new_parsed_policy()`, line preprocessing, `parse_version()`, `parse_header()`, `parse_operation()`, `parse_action()`, `parse_property()`, `parse_rule()`, `free_rule()`, and `validate_policy()`.

Control flow: The parser duplicates NUL-terminated policy text, splits on newline/CR, strips comments and trailing spaces, parses the first non-empty line as ordered `policy_name=` then `policy_version=`, then parses rules. Rule syntax requires optional leading `DEFAULT`, operation before properties, and action as the final token. Default rules cannot have properties. Non-default rules are appended to operation tables. Validation requires either a global default action or per-operation defaults for every operation.

State and persistence: Allocates parsed policy, name string, rules, properties, and digest values. Freeing walks all operation rule lists and frees digest-backed properties.

Dependencies and integration: Uses kernel match token parser, digest parser, policy type definitions, and IPE lifecycle code.

Risks and test signals: Risks include strict token ordering surprises, `while (t = strsep(...), line)` relying on final token handling, embedded NUL truncation, duplicate defaults, and digest property parse behavior. `policy_tests.c` covers many syntax failures; additional evaluator tests should verify semantic ordering and provider-disabled properties.
