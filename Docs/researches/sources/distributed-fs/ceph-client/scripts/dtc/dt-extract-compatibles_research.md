# sources/distributed-fs/ceph-client/scripts/dtc/dt-extract-compatibles

## Purpose
`dt-extract-compatibles` extracts device-tree compatible strings from C source files or directories by scanning common OF match tables, OF declaration macros, and compatible-lookup helper calls.

## Important APIs, Types, and Functions
`parse_of_declare_macros()`, `parse_of_device_id()`, `parse_of_match_table()`, and `parse_of_functions()` implement regex extraction. `parse_compatibles()` applies normal or driver-match filtering. `parse_compatibles_to_ignore()` collects non-driver OF declarations to suppress. `glob_without_symlinks()` and `files_to_parse()` discover `.c` files.

## Control Flow and State
Argparse accepts files/directories, `--with-filename`, and `--driver-match`. In driver-match mode it first builds an ignore list from all inputs, then parses each file and prints either one compatible per line or filename-prefixed summaries. State is transient lists.

## Dependencies and Integration
It depends on Python 3, regexes, filesystem walking, and Linux OF coding conventions. It is used by device tree binding and driver coverage workflows.

## Risks and Test Signals
The scanner removes newlines and uses regexes rather than a C parser, so macros, comments, nested braces, generated strings, and multiline constructs can be missed or misread. Directory pruning mutates `dirs` during iteration. Test OF tables with and without `of_match_ptr`, declaration macros, helper calls, driver-match filtering, hidden directories, and malformed source snippets.
