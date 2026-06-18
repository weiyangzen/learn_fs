# sources/distributed-fs/openafs/src/util/tabular_output.h

Purpose: Defines constants for the table output utility.

Important constants: Cell and allocation bounds are `UTIL_T_MAX_CELLS`, `UTIL_T_MAX_CELLCONTENT_LEN`, and `UTIL_T_NUMALLOC_ROW`. Content types are string and numeric. Output types are ASCII, CSV, and HTML. ASCII separators and command-help strings are also defined.

Control flow and state: Header-only constants; public function prototypes are not present in this header, so callers likely rely on prototypes from another aggregate header such as `afsutil.h`.

Dependencies and integration: Used by `tabular_output.c` and command-line tools that accept output-format or sort options.

Risks and test signals: The fixed 30-character cell size is a behavioral limit and a safety risk when implementation uses unchecked copies. `UTIL_T_TYPE_MAX` must track output-type constants. Tests are compile coverage and formatting tests through command consumers.
