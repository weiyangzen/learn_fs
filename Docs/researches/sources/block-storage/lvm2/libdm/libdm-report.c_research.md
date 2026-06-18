# File Research: sources/block-storage/lvm2/libdm/libdm-report.c

Purpose: implements libdevmapper's generic reporting engine: report-handle setup, field formatting, output field and sort-key parsing, object-to-row conversion, report selection/filter parsing and evaluation, compact output, tabular/rows/JSON output, and grouped report lifecycle.

Read coverage: complete file read, 5,644 lines.

Key responsibilities:
- Defines the internal report model: `struct dm_report`, report groups, group items, field properties, rows, report fields, selection nodes, selection values, reserved-value wrappers, and string-list sort metadata.
- Converts common field value types into display strings plus raw sort/filter values through helpers such as `dm_report_field_string()`, `dm_report_field_percent()`, `dm_report_field_string_list()`, `dm_report_field_string_list_unsorted()`, `dm_report_field_int()`, `dm_report_field_uint32()`, `dm_report_field_int32()`, `dm_report_field_uint64()`, and `dm_report_field_set_value()`.
- Parses requested output fields and sort keys, including canonicalized field names, optional report-type prefixes, implicit special fields, `all` expansion, ascending/descending key prefixes, duplicate sort-field handling, and hidden sort-only fields.
- Initializes and frees report handles through `dm_report_init()`, `dm_report_init_with_selection()`, and `dm_report_free()`, using `dm_pool` allocation for report-owned state and separate pools for parsed selections and compiled regexes.
- Builds report rows from caller-supplied objects in `_do_report_object()`, calling each registered field's object-type data function and report callback, then evaluating selection rules before buffering or immediately outputting rows.
- Implements selection parsing for field comparisons, logical operators, negation, parentheses, string lists, regexes, numeric/size/percent values, formatted times, epoch times, and reserved values.
- Evaluates selections across strings, numbers, sizes, percents, times, regexes, and string lists, including strict list matching, subset list matching, all/any list semantics, blank-list handling, and reserved-value exclusions.
- Supports compact output by hiding globally empty fields or selected empty fields after buffered rows have been collected.
- Calculates column widths, emits optional headings, sorts rows, and outputs reports as normal columns, columns-as-rows, basic grouped reports, legacy JSON, or JSON_STD.
- Manages report groups through `dm_report_group_create()`, `dm_report_group_push()`, `dm_report_group_pop()`, `dm_report_group_output_and_pop_all()`, and `dm_report_group_destroy()`.

Important public entry points:
- Report lifecycle: `dm_report_init()`, `dm_report_init_with_selection()`, `dm_report_free()`.
- Field value helpers: `dm_report_field_*()`, `dm_report_field_set_value()`.
- Object reporting: `dm_report_object()`, `dm_report_object_is_selected()`, `dm_report_destroy_rows()`, `dm_report_is_empty()`.
- Output control: `dm_report_output()`, `dm_report_column_headings()`, `dm_report_compact_fields()`, `dm_report_compact_given_fields()`, `dm_report_set_output_field_name_prefix()`.
- Selection and value utilities: `dm_report_set_selection()`, `dm_percent_to_float()`, `dm_percent_to_round_float()`, `dm_make_percent()`, `dm_report_value_cache_set()`, `dm_report_value_cache_get()`.
- Grouped output: `dm_report_group_create()`, `dm_report_group_push()`, `dm_report_group_pop()`, `dm_report_group_output_and_pop_all()`, `dm_report_group_destroy()`.

Core data flow:
- A caller registers report object types and field definitions, then calls `dm_report_init()` or `dm_report_init_with_selection()` with requested output fields, separator, output flags, sort keys, private data, optional selection, and optional reserved values.
- Initialization canonicalizes field IDs, parses output fields and keys once to infer report types, parses them again to populate `rh->field_props`, and records implicit fields such as `help`, `?`, and, with selection enabled, `selected`.
- For each object, `_do_report_object()` allocates a row, creates a `dm_report_field` per configured field, fetches field data through the field's object-type `data_fn`, invokes the field `report_fn`, and checks the parsed selection tree.
- Selected rows, or rows that must be kept for a visible `selected` field or multiple-output reports, are buffered or immediately passed to `dm_report_output()`.
- Output recalculates widths and sort slots when needed, optionally sorts buffered rows, then emits headings and rows in the active format before destroying row allocations unless multiple-output reuse is enabled.

Selection language:
- Comparison operators include equality/inequality, regex match/non-match, numeric greater/less variants, and time aliases such as `since`, `after`, `until`, and `before`.
- Logical operators include `&&` and `,` for AND, `||` and `#` for OR, `!` for negation, parentheses for grouping, `[]` for strict string-list comparisons, and `{}` for subset string-list comparisons.
- Field values are tokenized as strings, regexes, string lists, non-negative numbers, sizes with optional units, percents with optional `%`, formatted ISO-like date/time values, or `@seconds_since_epoch`.
- Size selections default to MiB when no unit is specified and are converted to sectors for comparison.
- Formatted time values support varying precision; reduced precision expands to a range covering the specified year, month, day, hour, minute, or second.
- Reserved values can be type-wide or field-specific, named, dynamic, fuzzy-name based, and optionally ranges. Strict reserved values are excluded from ordinary comparison values.

Output behavior:
- Basic text output can be aligned or unaligned, optionally include field-name prefixes, quote values, print headings, buffer for sorting, or display columns as rows.
- JSON output is coordinated through report groups. The JSON group code opens named arrays, rejects interleaved JSON reports, tracks indentation, closes arrays/objects on pop, and forces JSON reports to be buffered and unaligned.
- JSON_STD differs from legacy JSON by emitting pure numeric number/percent fields without quotes, outputting empty pure-numeric fields as `null`, and outputting string-list fields as proper JSON arrays.
- JSON_STD creation checks the locale radix character and refuses locales whose decimal separator is not `.`.
- String output for JSON escapes quotes and backslashes but otherwise writes the report string through `_safe_repstr_output()`.

Memory and lifetime:
- `dm_report` itself is allocated with `dm_zalloc`; most report internals and rows are allocated from `rh->mem`, a report memory pool.
- The first row allocation is cached in `rh->first_row`; freeing it releases all later row and field allocations made from the same pool region.
- Parsed selection nodes and values live in `rh->selection->mem`; compiled regex state lives in `rh->selection->regex_mem`.
- `dm_report_free()` destroys selection pools, the optional value cache, the report memory pool, and the report structure.
- Group state lives in a separate group pool and temporarily rewrites report flags while a report is pushed into a group; pop restores the original report flags and clears `report->group_item`.

Dependencies:
- Includes `libdm/misc/dmlib.h` and standard headers for character classification, locale information, math, floating-point epsilon, and time handling.
- Uses libdm allocation, lists, pools, hashes, regexes, bitsets, unit parsing, logging, and percent constants.
- Consumes caller-provided `dm_report_object_type`, `dm_report_field_type`, and `dm_report_reserved_value` definitions from the public libdm reporting API.
- Depends on registered field callbacks to provide correctly typed `report_string` and `sort_value` values matching each field's declared flags.

Risk and edge cases:
- The reporting engine trusts field definitions and report callbacks heavily; mismatched field flags, offsets, data functions, or sort-value types can break sorting and selection.
- Selection parsing mutates temporary input buffers in a few reserved-value and field-name error paths by writing a temporary NUL, so callers should pass mutable or safely owned strings where expected by this API's historical contract.
- `_implicit_report_fields` is file-global and is switched to the selection-aware implicit field table by `dm_report_init_with_selection()`, so implicit-field behavior is process-global rather than per-report.
- JSON output requires strict push/pop ordering; interleaved reports in a JSON group are explicitly rejected.
- Buffered reports can retain rows for multiple outputs, and `dm_report_set_selection()` reevaluates existing rows, so callers using `DM_REPORT_OUTPUT_MULTIPLE_TIMES` need to manage row lifetime intentionally.
- Compact output only works on buffered reports with collected rows; calling it before rows exist or on non-buffered reports is effectively a no-op.
- String-list report strings carry hidden `struct pos_len` metadata after the terminating NUL. Output and selection code depend on that layout, so custom field helpers must preserve the expected `sort_value` shape for string-list fields.
- Time parsing accepts only supported ranges and requires a full date before time-of-day components; timezone handling adjusts supplied absolute GMT offsets into local time.
- JSON escaping covers quotes and backslashes; control-character handling depends on upstream report strings avoiding problematic raw control bytes.
