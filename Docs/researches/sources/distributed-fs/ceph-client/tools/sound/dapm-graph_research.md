# sources/distributed-fs/ceph-client/tools/sound/dapm-graph

Purpose: shell tool that converts ALSA ASoC DAPM debugfs state into a Graphviz dot graph, optionally rendering it to an image format.

Important APIs, types, and functions: functions are `usage()`, `grab_remote_files()`, `process_dapm_widget()`, `process_dapm_component()`, `process_dapm_tree()`, and `main()`. Style variables define colors and node attributes for powered/unpowered components and widgets. The tool supports local card debugfs (`-c`), remote collection over ssh/scp (`-c` plus `-r`), or a local debugfs mirror (`-d`), with `-o` output and `-D` debug logging.

Control flow: `main()` validates exactly one input mode, creates a temporary directory, optionally collects remote debugfs files into a tarball because direct recursive scp would copy empty debugfs files, then calls `process_dapm_tree()`. The tree processor writes a dot header, processes the root card DAPM directory and each component `*/dapm`, and appends widget nodes plus input-link edges. Widget parsing reads the first line for power state, scans for `widget-type` and `in` routes, and writes dot node/edge records. The final dot file is copied to the requested `.dot` path or rendered with `dot -T<ext>`.

State and persistence: persistent output is the dot file and optional rendered file. Temporary state lives under `mktemp -d` and is removed on INT/TERM/EXIT. Debugfs state is read-only except remote commands create temporary copies on the target path supplied by `tmp_dir`.

Dependencies and integration points: depends on `/sys/kernel/debug/asoc/<card>`, shell utilities (`find`, `tar`, `awk`, `sed`, `grep`, `basename`), ssh/scp for remote mode, and Graphviz `dot` for non-dot output. It integrates with ASoC DAPM debugfs file formats.

Risks: widget and route parsing is text-format sensitive and only escapes newline labels via a `%` placeholder, not general Graphviz special characters. The `usage` call on missing output extension is invoked without an explicit status in one path. Remote collection assumes the local temp path is also valid on the remote target. The `for w_file in ${c_dir}/*` loop can mis-handle names with whitespace.

Test signals: with a saved debugfs tree, `-d <tree> -o dapm.dot` should produce valid dot. Non-dot output should also create the dot sidecar and rendered image. Debug mode should list components, widget types, and routes.
