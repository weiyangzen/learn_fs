
# sources/distributed-fs/ceph-client/tools/perf/util/parse-events.l

Purpose: flex lexer for perf event syntax. It tokenizes full event lists and standalone config term lists for the bison grammar in `parse-events.y`.

Important APIs/types/functions: lexer options make it reentrant, bison-bridge/location-aware, prefixed with `parse_events_`, and no-yywrap. Helper functions parse numeric values, duplicate names and quoted names, strip `@` driver-config strings, rewind matched event text, emit static term tokens, and parse event modifiers into `struct parse_events_modifier`. Start conditions separate `event`, `config`, and `mem` modes.

Control flow: the first token is controlled by `parse_events_state->stoken`, switching to event or config mode and returning `PE_START_EVENTS` or `PE_START_TERMS`. In event mode, grouped or PMU-style text is rewound for grammar-level parsing, while commas are emitted directly. In config mode, known term names become `PE_TERM`, raw encodings become `PE_RAW`, driver terms become `PE_DRV_CFG_TERM`, and slash exits config mode. In `mem` mode, breakpoint modifiers and length separators are disambiguated from event modifiers and PMU config slashes. Global rules tokenize `mem:`, raw hex, numbers, modifiers, names, quoted names, braces, colon, equals, and commas.

State and persistence: uses scanner-local yylval/yylloc and parse-state extra data. Allocated strings are owned by bison semantic values and released by destructors/actions.

Dependencies: generated bison header, `parse-events.h`, errno/stdlib/stdio, and flex location/column support.

Integration points: generated into `parse-events-flex.*` and used by `parse_events__scanner`. It defines the accepted CLI syntax for event names, groups, modifiers, PMU config terms, raw events, and memory breakpoint syntax.

Risks: token regex changes directly alter user-visible event parsing. Modifier letters must stay disjoint from breakpoint modifiers where assumed and synchronized with semantic handling. Quoted-name support is intentionally narrow. Bad numeric conversion emits parser errors. Test signals include event parser tests for each syntax family, config-term parsing, quoted names, driver-config terms, duplicate modifiers, memory breakpoints, and raw event encodings.
