<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/parse-headers.py -->
# sources/distributed-fs/ceph-client/tools/docs/parse-headers.py

Purpose: Converts a C source/header into ReST containing a parsed-literal or TOC table, enriching detected C API names with cross-references and optional override rules.

Important APIs/types/functions: `main()` parses `file_in`, `file_out`, optional `file_rules`, `--debug`, and `--toc`. It uses kernel-local `kdoc.parse_data_structs.ParseDataStructs` to identify defines, ioctls, functions, structs, typedefs, enums, and enum symbols. `kdoc.enrich_formatter.EnrichFormatter` formats argparse help from the module docstring.

Control flow: The script constructs a parser object, reads and applies optional rules through `parse_file()`, optionally emits debug data, then writes the converted RST with `write_output()`.

State and persistence: The input parse tree is transient. Persistent output is the requested RST file. Rule files can suppress or replace generated references, making output dependent on external policy files.

Dependencies/integration: Used by kernel documentation to include UAPI/header listings with stable cross references. Depends on `tools/docs/lib/python/kdoc` modules and source/rules files.

Risks/tests: Risks include incorrect C construct detection, rule-file drift, and generated cross-reference churn that breaks Sphinx builds. Test signals are golden output for representative headers, `--toc` mode, rules for `ignore` and `replace`, and Sphinx nitpicky build warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/parse-headers.py -->
