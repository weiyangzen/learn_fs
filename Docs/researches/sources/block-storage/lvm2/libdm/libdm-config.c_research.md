# File Research: sources/block-storage/lvm2/libdm/libdm-config.c

## Purpose

`libdm-config.c` implements libdm’s lightweight hierarchical configuration parser, writer, lookup API, cloning helpers, and cascade/flatten support. It parses LVM-style config syntax into `struct dm_config_tree`, `struct dm_config_node`, and `struct dm_config_value` objects allocated from a `dm_pool`.

## Main Responsibilities

- Create and destroy config trees backed by a memory pool.
- Parse text config into a tree:
  - sections delimited by `{` and `}`,
  - key/value assignments,
  - arrays,
  - integers,
  - floats,
  - quoted strings,
  - escaped double-quoted strings,
  - bare strings in value context,
  - comments starting with `#`.
- Write config trees back through line callbacks or output specs.
- Find nodes and typed values by slash-separated paths.
- Support cascaded config trees where earlier trees override later trees.
- Clone nodes and values into a target memory pool.
- Flatten cascaded trees into one merged tree.
- Remove nodes from a parent’s child list.

## Parser Structures

- `struct parser`
  - Tracks buffer bounds, current token, line number, memory pool, duplicate-node behavior, stop-after-section state, and section nesting.
- `struct config_output`
  - Holds output memory pool, line callback, optional node output spec, and baton.

## Token Model

The tokenizer emits:
- `TOK_INT`
- `TOK_FLOAT`
- `TOK_STRING`
- `TOK_STRING_ESCAPED`
- `TOK_STRING_BARE`
- `TOK_EQ`
- `TOK_SECTION_B`
- `TOK_SECTION_E`
- `TOK_ARRAY_B`
- `TOK_ARRAY_E`
- `TOK_IDENTIFIER`
- `TOK_COMMA`
- `TOK_EOF`

Token interpretation depends on context. After `=`, `[`, or `,`, numeric-looking tokens may become integers/floats and non-delimited tokens may become bare strings. Outside value context, similar text is treated as identifiers.

## Important Functions

- `dm_config_create()` allocates the config pool and root tree object.
- `dm_config_destroy()` destroys the backing pool.
- `dm_config_set_custom()` / `dm_config_get_custom()` store caller-owned context.
- `dm_config_insert_cascaded_tree()` and `dm_config_remove_cascaded_tree()` manage the cascade link.
- `dm_config_parse()` parses with duplicate-node checking.
- `dm_config_parse_without_dup_node_check()` disables duplicate checking.
- `dm_config_parse_only_section()` parses one named section and only top-level non-section nodes after it, intended for metadata scanning.
- `dm_config_from_string()` creates and parses a tree from a null-terminated string.
- `dm_config_write_one_node()`, `dm_config_write_node()`, `dm_config_write_one_node_out()`, `dm_config_write_node_out()` serialize nodes.
- `_section()`, `_value()`, `_type()`, `_get_token()`, `_eat_space()` implement the parser.
- `_find_or_make_node()` finds existing path segments or creates them when given a memory pool.
- `dm_config_find_node()`, `dm_config_find_int()`, `dm_config_find_int64()`, `dm_config_find_float()`, `dm_config_find_bool()`, `dm_config_find_str()`, `dm_config_find_str_allow_empty()` are node-rooted lookup helpers.
- `dm_config_tree_find_node()` and corresponding `dm_config_tree_find_*()` helpers search through cascaded trees.
- `dm_config_get_uint32()`, `dm_config_get_uint64()`, `dm_config_get_str()`, `dm_config_get_list()`, `dm_config_get_section()` provide typed success/fail APIs.
- `dm_config_maybe_section()` heuristically checks whether a text buffer may contain a balanced config section.
- `dm_config_clone_node_with_mem()` and `dm_config_clone_node()` deep-copy node/value structures.
- `dm_config_create_node()`, `dm_config_create_value()`, `dm_config_memory()` expose construction helpers.
- `dm_config_flatten()` merges cascaded trees into a new tree by enumerating lower-priority trees first and overriding paths from higher-priority trees.
- `dm_config_remove_node()` unlinks a child node from a parent.

## Serialization Behavior

`_write_config()` emits one line per node:
- Sections emit `key {`, recursively emit children, then `}`.
- Values emit `key=value`.
- Lists emit `[item, item]`.
- Formatting flags influence quoting, octal integer output, array formatting, and extra spaces.
- Keys containing `#`, `"`, or `!` are double-quoted and escaped.
- String values are double-quoted unless `DM_CONFIG_VALUE_FMT_STRING_NO_QUOTES` is set.

Output can go to a simple `dm_putline_fn` or a richer `dm_config_node_out_spec` with prefix, line, and suffix callbacks.

## Lookup and Cascading

Path lookup uses slash-separated segments. `_find_config_node()` searches within one node tree. `_find_first_config_node()` walks `cft->cascade`, returning the first matching node. Typed lookup functions return caller-provided fallback values when absent or mismatched. Unsupported string values are warned in `_find_config_str()` when appropriate.

`dm_config_flatten()` builds a new tree by walking cascade tail-to-head so earlier/high-priority trees override later/lower-priority trees at identical paths.

## Memory Ownership

All parsed nodes and values live in the tree’s `dm_pool`. Destroying the tree frees the entire parse result. String config values are allocated in the same object block as their `dm_config_value`; node keys similarly follow their `dm_config_node` allocation. Cloning into a supplied memory pool preserves this allocation model.

## Notable Edge Cases

- Duplicate config nodes are warned and ignored unless duplicate checking is disabled.
- Duplicate values overwrite `root->v` after warning.
- Empty arrays are represented by a special `DM_CFG_EMPTY_ARRAY` value.
- Invalid 32-bit-era `creation_time` overflow is repaired to `1527120000` with a warning, preserving compatibility with old metadata.
- `dm_config_maybe_section()` is only a heuristic based on balanced `{` and `}` counts.
- `dm_config_remove_node()` only unlinks; memory remains owned by the pool.
