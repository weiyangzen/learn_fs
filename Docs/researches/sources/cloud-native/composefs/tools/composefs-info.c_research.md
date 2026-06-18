# sources/cloud-native/composefs/tools/composefs-info.c

## Purpose
`composefs-info.c` is an inspection CLI for composefs images. It can list tree paths, dump a machine-readable tree format, list referenced objects, list missing objects relative to a basedir, and measure fs-verity digests for ordinary files.

## Important APIs, Types, And Functions
The command dispatch uses `command_handler_init`, `command_handler`, and `command_handler_end` function pointers. Output helpers include `print_escaped`, `print_escaped_optional`, `print_node`, `dump_node`, and `node_build_path`. Object collection uses `PrintData`, libcomposefs hash table functions, `get_objects`, `print_objects_handler_init`, `print_objects_handler`, `print_missing_objects_handler`, and `print_objects_handler_end`. `measure_files` calls `lcfs_fd_get_fsverity` and `digest_to_string`.

Global options include `--basedir` and repeatable `--filter`, with filters passed through `lcfs_read_options_s.toplevel_entries`.

## Control Flow
`main` parses options, creates a C locale for stable escaping, selects a command, optionally opens the basedir as `O_DIRECTORY | O_PATH`, initializes handler data, then iterates over image paths. Each image is opened, loaded through `lcfs_load_node_from_fd_ext`, and passed to the selected handler. `objects` and `missing-objects` collect payloads in a hash table and print sorted unique entries at the end.

## State And Persistence
The tool is read-only except for stdout/stderr. State is process-local: filters, basedir fd, locale, hash table, and loaded node trees. The `missing-objects` command consults the filesystem through `fstatat` but does not modify it.

## Dependencies And Integration Points
It depends on libcomposefs node readers, digest helpers, internal hash table code, and locale/ctype APIs. Its `dump` output is accepted by `mkcomposefs --from-file`, making this file part of a textual interchange path for composefs trees.

## Risks
Escaping rules are central to interoperability with `mkcomposefs`; changes can break dump/import round trips. `missing-objects` treats payloads as relative by stripping leading slashes, so path expectations must match object-store conventions. The line `const char *image_path = image_path = argv[i];` is odd but benign C assignment syntax. Filters reject names containing `/`, limiting scope to top-level entries.

## Test Signals
Tests should cover `ls`, `dump`, `objects`, `missing-objects`, `measure-file`, escaping of spaces, equals signs, lone dashes, binary-ish xattr values, hardlinks, inline content, filtered top-level entries, and missing-object detection against a temporary basedir.
