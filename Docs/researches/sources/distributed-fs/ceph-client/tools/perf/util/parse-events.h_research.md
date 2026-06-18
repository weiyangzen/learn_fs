
# sources/distributed-fs/ceph-client/tools/perf/util/parse-events.h

Purpose: declares perf event parser types, term enums, state structs, modifiers, error handling, and APIs used by CLI option handling, PMU alias code, metric parsing, and tests.

Important APIs/types/functions: `parse_events_option_args` carries evlist pointer and optional PMU filter. `parse_events_term` models config terms with config name, numeric/string value, predefined term type, parse columns, weak/used/no-value flags. `parse_events_terms` wraps a list. `parse_events_state` carries destination list, next index, error list, term result, start token, fake modes, PMU filter, legacy-cache matching, and wildcard-PMU status. `parse_events_modifier` stores parsed modifier letters. The header exposes parser entry points, filters, term constructors/destructors, term parsing, modifier application, event creation helpers, multi-PMU expansion, leader setup, error APIs, SDT event detection, and breakpoint length helper.

Control flow: no executable flow besides inline `parse_events`, which calls `__parse_events` with default PMU filter and real PMU/tracepoint modes. The `is_sdt_event` inline detects SDT/cached probe syntax only when ELF support is enabled.

State and persistence: defines transient parser and error state. Terms own strings and must be freed with `parse_events_terms__exit/delete`; errors own message/help strings until exit.

Dependencies: Linux list/types/perf_event, booleans, string/sys types, and forward declarations for perf PMU/evsel/evlist/option/strbuf.

Integration points: included by `parse-events.c`, flex/bison generated code, PMU code, metricgroup, CLI option files, and tests.

Risks: enum values must stay synchronized with lexer term names and `parse_events__term_type_str`. Adding modifiers requires updates in lexer, struct fields, and semantic handling. Inline SDT detection is build-feature dependent. Test signals are full event parser build/test coverage and static checks that term-name tables and enums remain aligned.
