# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-mkspace.c

Purpose: `pvfs2-mkspace.c` creates or removes OrangeFS storage spaces and collections by wrapping the lower-level `mkspace.h` helpers. It is used during filesystem provisioning and destructive cleanup.

Important APIs, types, and functions: `options_t` captures defaults flag, verbosity, collection id/name, root handle, collection-only mode, delete-storage mode, handle ranges, and data/metadata storage paths. `parse_args` handles short and long options, `print_options` reports the effective config, `print_help` documents defaults, and `main` calls either `pvfs2_mkspace` or `pvfs2_rmspace`. Default ranges are `4-2147483650` for metadata and `2147483651-4294967297` for data, with default collection name `pvfs2-fs`.

Control flow: with no args the tool prints help and exits failure. Parsing supports `--data-space`, `--meta-space`, `--coll-id`, `--coll-name`, `--root-handle`, `--delete-storage`, `--meta-handle-range`, `--data-handle-range`, `--add-coll`, `--defaults`, version, help, and verbose. If defaults are requested, selected fields are overwritten with static defaults. The program prints options, validates that data space, metadata space, collection id, and at least one handle range are present, then dispatches to remove or create.

State and persistence: this is a persistent storage-space mutator. `pvfs2_mkspace` creates Trove/storage directories and collection metadata, while `pvfs2_rmspace` removes them when `--delete-storage` is passed. `--add-coll` limits operation to collection creation/removal inside an existing storage space.

Dependencies and integration points: it depends on `mkspace.h` and the storage backend implementation behind `pvfs2_mkspace`/`pvfs2_rmspace`. Generated configuration from `pvfs2-genconfig` must agree with collection id, collection name, root handle, handle ranges, and storage paths used here.

Risks: `--delete-storage` is explicitly unrecoverable, but there is no confirmation prompt. `--defaults` does not set data or metadata storage paths or collection id, so it is not a full standalone default mode. The create path prints `opts.collection_only(%d).` as debug noise. Numeric parsing uses `strtoull`/`strtoul` without end-pointer validation, so malformed values can become zero. `strncpy` calls may leave nonterminated strings if optarg length reaches `PATH_MAX - 1` in some paths. A missing root handle defaults to `PVFS_HANDLE_NULL`, which may or may not be valid depending on helper behavior.

Test signals: dry-run style tests should isolate temp data/meta spaces. Cover missing required paths, defaults plus explicit required options, create storage, add collection, delete collection-only, delete full storage, invalid collection id/root handle/range text, long path truncation, verbose mode, and compatibility with configs emitted by `pvfs2-genconfig`.
