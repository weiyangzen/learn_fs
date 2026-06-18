# sources/distributed-fs/ceph-client/scripts/extract-ikconfig

Purpose: Extracts embedded `.config` data from a kernel image built with `CONFIG_IKCONFIG`.

Important APIs/functions: `dump_config()` locates the `IKCFG_ST` gzip signature and pipes from that offset through `zcat`. `try_decompress()` scans for compression magic, decompresses candidate streams into a temp file, and retries `dump_config()`.

Control flow: Validates exactly one non-empty image argument, creates `/tmp/ikconfig$$.*` temp files with a cleanup trap, first tries direct extraction, then tries gzip, xz, bzip2, lzma, lzop, lz4, and zstd container signatures. On success it prints config and exits 0; otherwise prints a failure message and exits 1.

State/persistence: Uses predictable `/tmp/ikconfig$$.1` and `.2` temp files removed on exit. Writes config to stdout.

Dependencies/integration: Shell, `tr`, `grep -abo`, `tail`, `zcat`, and optional decompressor commands. Used by developers/debug scripts to recover kernel configs.

Risks: Predictable temp filenames can collide in unusual same-PID namespace scenarios. Missing decompressors are silently skipped via redirected errors. Magic scanning can false-positive and repeatedly invoke decompressors. It assumes gzip-wrapped config format.

Test signals: Test uncompressed object/image, each supported compressed wrapper, missing config, invalid args, and images with multiple compression magic candidates.
