
# sources/distributed-fs/ceph-client/tools/perf/util/parse-events.y

Purpose: bison grammar for perf event lists and config term lists. It assembles lexer tokens into evsel lists and config-term objects by invoking semantic helpers in `parse-events.c`.

Important APIs/types/functions: grammar values include strings, numbers, `parse_events_modifier`, term types, evsel lists, term lists, term objects, and tracepoint name pairs. It defines destructors for strings, terms, term lists, evsel lists, and tracepoint names. Helper `alloc_list` creates list heads and `free_list_evsel` deletes evsels on grammar cleanup.

Control flow: entry `start` switches between `start_events` and `start_terms`. `groups` combines groups and events separated by commas. `group_def` sets the first event as leader and optional group name. `event_mod` applies event modifiers; `group` can apply group modifiers. `event_pmu` handles PMU names, PMU configs, or event-name multi-PMU expansion. Legacy forms cover `mem:` breakpoints, `sys:event` tracepoints, numeric `type:config`, and raw `rNNN` events. `event_config` builds term lists from assignments, no-value terms, built-in terms, and driver-config terms.

State and persistence: successful event parsing splices owned evsels into `parse_state->list`; successful term parsing stores a term list in `parse_state->terms`. Destructors clean up on parse abort.

Dependencies: PMU/PMU registry headers, evsel deletion, parse-events semantic API, Linux types, and generated lexer token declarations.

Integration points: generated parser is called by `parse_events__scanner` for both CLI event strings and sysfs/alias term parsing. It is the formal syntax contract for groups, modifiers, PMU config, tracepoint, raw, numeric, and memory breakpoint event forms.

Risks: grammar ambiguity around slashes/colons is coordinated with lexer states; changes can break legacy syntax. Ownership transfer between grammar actions and destructors is delicate. Errors use `PE_ABORT` to distinguish OOM from semantic invalidity. Test signals are parser regression tests across all event syntaxes, OOM/error cleanup checks, group leader/name behavior, and term-list parsing tests.
