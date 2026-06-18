# sources/distributed-fs/orangefs/src/common/misc/server-config.c

## Purpose

`server-config.c` is the OrangeFS/PVFS2 configuration parser and runtime accessor implementation for server and client-visible filesystem configuration. It binds dotconf option names to callback handlers, builds `server_configuration_s` and nested `filesystem_configuration_s` objects, validates alias/range/filesystem relationships, exposes lookup helpers used by server startup and request paths, and, when Trove support is compiled, creates or removes on-disk storage spaces from parsed configuration.

The file is stateful in the sense that parsing mutates one caller-provided `server_configuration_s`. It is not a persistent store itself, but it reads and caches the config file contents, keeps parsed strings/lists/ranges in heap-owned structures, and passes storage-space creation/removal requests to `pvfs2_mkspace()` and `pvfs2_rmspace()`.

## Important APIs and functions

- `PINT_parse_config(config_obj, global_config_filename, server_alias_name, server_flag)` zeroes the caller's config object, applies built-in defaults, caches the fs.conf file, creates a dotconf parser with the local `options[]` table, runs the parse loop, resolves the selected server alias to `host_id`, and checks required fields such as storage paths, BMI modules, flow modules, performance settings, and security key/cert paths depending on compile flags.
- `PINT_config_release(config_s)` frees heap allocations owned by a parsed config, including aliases, filesystem lists, cached file data, module strings, export lists, security paths, and trusted-network data.
- `PINT_config_is_valid_configuration()` validates global fields and all configured filesystems, primarily checking that each root handle is in one configured metadata handle range.
- `PINT_config_get_host_addr_ptr()` and `PINT_config_get_host_alias_ptr()` translate between host aliases and BMI address strings. Returned pointers are borrowed from the config object.
- `PINT_config_get_meta_handle_range_str()`, `PINT_config_get_data_handle_range_str()`, and `PINT_config_get_merged_handle_range_str()` return host-specific handle range strings for a filesystem. The merged version allocates a new string for the caller to free.
- `PINT_config_get_meta_handle_extent_array()` copies the current host's metadata handle extent array for a filesystem id into caller-owned memory.
- `PINT_config_find_fs_name()`, `PINT_config_find_fs_id()`, `PINT_config_get_fs_id_by_fs_name()`, and `PINT_config_get_filesystems()` are runtime lookup helpers over the parsed filesystem list.
- `PINT_config_trim_filesystems_except()` replaces the full filesystem list with a deep copy of one selected filesystem, preserving alias pointers and duplicating the selected filesystem's nested fields.
- `PINT_config_get_fs_key()` decodes a filesystem `SecretKey` from base64 with OpenSSL when available. Without OpenSSL it reports `-PVFS_ENOSYS`.
- Trove-gated APIs `PINT_config_pvfs2_mkspace()`, `PINT_config_pvfs2_rmspace()`, `PINT_config_get_trove_sync_meta()`, and `PINT_config_get_trove_sync_data()` integrate parsed configuration with storage creation/removal and storage sync hints.

Most other functions are dotconf callbacks named after config options, for example `get_bmi_module_list`, `get_range_list`, `get_root_squash`, `get_trove_method`, `get_db_max_size`, `get_ldap_search_mode`, and context enter/exit callbacks.

## Control flow

The central control path starts in `PINT_parse_config()`. It initializes defaults on `server_configuration_s`, reads the config file into `fs_config_buf`, creates a `configfile_t` with the local `options[]` array, installs `errorhandler` and `contextchecker`, then runs `PINT_dotconf_command_loop()`. The dotconf table encodes each option's name, argument type, callback, legal context mask, and default. `contextchecker()` rejects options used outside the current context mask.

Context callbacks set `config_s->configuration_context` as dotconf enters and leaves nested sections. `<Defaults>` also triggers dotconf defaults for both security and default contexts. `<FileSystem>` allocates a new zeroed `filesystem_configuration_s`, fills base filesystem defaults, inserts it at the head of `config_s->file_systems`, and applies filesystem defaults. `</FileSystem>` checks that name, collection id, root handle, and both handle-range lists were supplied. `<ServerOptions>` applies defaults and then option callbacks ignore values unless `check_this_server()` matched the configured alias and set `my_server_options`.

Option callbacks mutate either the global `server_configuration_s` or the current filesystem at the head of `file_systems`. List options such as aliases, module lists, export host lists, precreate sizes, and handle ranges allocate new arrays or strings. Handle range parsing validates aliases, validates the textual range characters, either finds an existing mapping or allocates a new mapping, merges repeated ranges with `PINT_merge_handle_range_strs()`, and rebuilds `PVFS_handle_extent_array` with `PINT_parse_handle_ranges()`.

After dotconf completes, `PINT_parse_config()` resolves `server_alias_name` through the alias list and records `host_id` and `host_index`. It then enforces server-side required fields. Later runtime helper calls walk `PINT_llist` lists linearly to retrieve aliases, filesystems, and range mappings.

## State and persistence behavior

The parser stores durable runtime state in heap allocations reachable from `server_configuration_s`. Ownership is mostly clear: `PINT_config_release()` owns strings and lists directly attached to config and filesystem objects. `host_handle_mapping_s.alias_mapping` is intentionally a borrowed pointer into the global alias list and is not freed by mapping cleanup. `PINT_config_get_*_ptr()` helpers return borrowed pointers, while `PINT_config_get_merged_handle_range_str()` and `PINT_config_get_meta_handle_extent_array()` allocate caller-owned results.

The file itself does not write config persistence. It caches the source config file in RAM through `cache_config_files()` so getconfig-style operations can return the original config without rereading the file. With `__PVFS2_TROVE_SUPPORT__`, `PINT_config_pvfs2_mkspace()` and `PINT_config_pvfs2_rmspace()` cause persistent storage side effects under parsed data and metadata paths.

## Dependencies and integration points

Dependencies include dotconf (`PINT_dotconf_create`, defaults, command loop), OrangeFS linked lists (`PINT_llist_*`), gossip logging, PVFS and Trove types, extent utilities (`PINT_create_extent_list`, `PINT_handle_in_extent_list`, `PINT_release_extent_list`), string utilities (`PINT_split_string_list`, `PINT_parse_handle_ranges`, `PINT_merge_handle_range_strs`), mkspace/rmspace storage helpers, and OpenSSL BIO base64 decoding when compiled.

Integration points are broad: server startup uses this parser to load fs.conf and server-specific options, storage initialization uses range and Trove settings, request paths use filesystem and alias lookup helpers, security layers use trusted ports/networks, key paths, cert settings, LDAP options, and filesystem secret keys, and flow/BMI/job layers consume module lists, timeouts, buffer sizes, and retry settings.

## Risks and edge cases

- Several string accumulation callbacks use fixed 512 or 2048 byte buffers with `strncat()` and hand-maintained lengths. They avoid obvious unbounded `strcat`, but the length accounting is inconsistent enough that oversized config values deserve tests.
- Many allocation failures are guarded with `assert()` rather than graceful error returns, especially in deep-copy paths. Release builds built with assertions disabled could continue with null pointers in some paths.
- `PINT_split_string_list()` can return early on empty comma elements without freeing already allocated token storage, so malformed comma lists can leak transient allocations.
- `get_range_list()` assumes alias/range arguments come in pairs and increments `i` inside the loop. Odd argument counts rely on dotconf/list behavior and assertions rather than explicit validation.
- `get_attr_cache_keywords_list()` deduplicates by `strstr(buf, rtok)`, so short key names could match substrings instead of exact comma-delimited tokens if future key names overlap.
- The parser mutates one config object and stores parse context in that object, so it is not reentrant for a shared object.
- `cache_config_files()` uses `PWD` rather than `getcwd()` on non-Windows fallback paths and only retries in unusual stat-error cases, so caller environment can affect diagnostics.
- Some callbacks treat invalid values as warnings and keep defaults, while others fail the parse. This is intentional legacy behavior but makes validation uneven.

## Test signals

Useful tests should parse representative fs.conf files covering Defaults, Security, LDAP, Aliases, ServerOptions, multiple FileSystem sections, StorageHints, ExportOptions, Distribution, and repeated Range entries. Assertions should check server-specific override gating, required-field failures, root-handle-in-meta-range validation, alias duplicate rejection, merged range strings and extent arrays, release after partial parse failure, trusted-network netmask parsing, invalid yes/no options, precreate list length enforcement, DBMaxSize context behavior, and Trove mkspace/rmspace argument selection with root handle only on the responsible metadata server.
