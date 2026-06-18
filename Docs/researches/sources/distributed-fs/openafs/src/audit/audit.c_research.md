# sources/distributed-fs/openafs/src/audit/audit.c

## Purpose
`audit.c` is the central audit formatter, dispatcher, and command-option parser for OpenAFS server audit events. It turns typed variadic audit arguments into text records and sends them to all configured audit interfaces; on AIX it can also use native audit records.

## Important APIs, types, and functions
Public functions from `audit.h` include `osi_audit`, `osi_auditU`, `osi_audit_cmd_Options`, `osi_audit_file`, `osi_audit_init`, `osi_audit_interface`, `osi_audit_set_user_check`, `audit_PrintStats`, `osi_audit_open`, and `osi_audit_close`. Important internal pieces are `struct audit_log`, `struct audit_msg`, `audit_interfaces`, `audit_logs`, `multi_send_msg`, `append_msg`, `printbuf`, `osi_audit_internal`, `osi_audit_check`, `parse_file_options`, and `parse_option_string`.

## Control flow
Callers configure auditing through `osi_audit_interface` and `osi_audit_file`, often via `osi_audit_cmd_Options`. `osi_audit_file` parses `[interface:]filespec[:options]`, creates a backend context, applies optional comma-separated options, opens the sink, and appends it to `audit_logs`. `osi_audit` and `osi_auditU` lazily call `osi_audit_check`, skip work when no audit mode/output is active, then format event data. `osi_auditU` extracts authenticated rxkad user and peer host information from an `rx_call`, emitting secondary audit events for unauthenticated, missing-name, unknown-security, or null-call cases. `printbuf` walks the variadic AUD_* stream and appends textual fields for strings, ids, hosts, FIDs, arrays, and butc tape structures before sending under the audit mutex.

## State and persistence
Process-global state includes the active backend queue, default interface index, audit enabled state from `AFSDIR_SERVER_AUDIT_FILEPATH`, a boolean indicating any open sink, and an optional local-user callback. Persistent output is backend-specific: files, FIFOs, SysV queues, or AIX audit logs. `osi_audit_check` reads the server `Audit` file and enables all-event auditing only when `AFS_AUDIT_AllEvents` appears.

## Dependencies and integration points
This file integrates rx/rxkad identity extraction, OpenAFS queue primitives, pthread mutex initialization, butc and AFS wire structures, audit backends via `audit-api.h`, and server command-line processing via `cmd_item`. Event names and AUD_* type tags are defined in `audit.h`.

## Risks
The API is variadic and depends on each AUD_* tag matching the following argument type exactly. Recursion is possible because `osi_auditU` emits audit events while auditing another event; `printbuf` suppresses timestamp/thread only when explicitly told but most paths use `rec == 0`. `parse_file_options` mutates its duplicated input and has custom handling for empty fields that should be preserved carefully. `auditout_open` is not reset in `osi_audit_close`, so post-close behavior depends on an empty backend list. Formatting truncation is tracked, but not all backends visibly mark truncated text.

## Test signals
Cover audit-on/off file detection, no-output fast path, all AUD_* format tags including null values, maximum-message truncation, multiple backends fanout, command option parsing for one/two/three-field forms, invalid interfaces/options, `osi_auditU` for null/rxnull/rxkad/unknown security classes, local realm callback behavior, close/open lifecycle, and pthread builds.
