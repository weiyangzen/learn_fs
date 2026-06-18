# sources/distributed-fs/ceph-client/tools/docs/gen-redirects.py

Purpose: Generates static HTML redirect pages for renamed documentation pages from `gen-renames.py` output.

Important APIs, types, and functions: Parses `--output`, reads stdin lines containing old and new documentation names without `Documentation/` and `.rst`, builds old/new `.html` paths, creates old output directories, computes relative target path, and writes a meta-refresh HTML file.

Control flow: For each stdin line, split into old and new names, skip with warning if target HTML does not exist, create parent directories as needed, and write redirect content pointing to relative new page.

State and persistence: Writes HTML files under the output directory.

Dependencies and integration points: Consumes `tools/docs/gen-renames.py` output and Sphinx-built HTML output. Uses Python os/sys only.

Risks: `line.split(' ', 2)` is unpacked into two variables, which will fail if a line contains more than one separator field; current producer emits exactly one space. Generated HTML does not escape names/paths. Requires target pages built before redirects.

Test signals: Pipe known rename pairs, verify relative links at nested depths, missing target warning, and malformed input handling.
