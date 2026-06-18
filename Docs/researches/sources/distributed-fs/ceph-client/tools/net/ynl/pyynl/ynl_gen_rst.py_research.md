# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/ynl_gen_rst.py

Purpose: command-line generator for RST documentation from YNL YAML specs. It is intentionally thin: validate arguments, invoke `YnlDocGenerator`, and write the generated text.

Important APIs/functions: `parse_arguments()` handles `--verbose`, `--output`, and mutually exclusive `--input`; it rejects missing output and non-file input. `write_to_rstfile()` writes UTF-8 content. `main()` constructs `YnlDocGenerator`, calls `parse_yaml_file()` for the input spec, catches broad parser failures, logs warnings, and exits with `-1`.

Control flow and state: no persistent state beyond the output file. Existing output is overwritten after a debug log. Verbose mode configures root logging to `DEBUG`.

Dependencies and integration: imports `YnlDocGenerator` from the sibling `pyynl/lib` package and depends on filesystem paths supplied by callers. It is part of the Linux YNL documentation toolchain and should be run from scripts or docs builds that provide a YAML spec and destination RST.

Risks and tests: the CLI currently defines only an input/output path, not an index mode despite a comment mentioning index/input. It catches all exceptions, which keeps CLI output simple but can hide exact stack traces unless verbose logging is used. Test signals are successful RST generation for representative YAML specs, missing-output rejection, invalid input rejection, and UTF-8 write verification.
