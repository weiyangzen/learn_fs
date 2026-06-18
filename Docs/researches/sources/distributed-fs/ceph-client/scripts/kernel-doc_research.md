# sources/distributed-fs/ceph-client/scripts/kernel-doc

## Purpose
`kernel-doc` is the Python 3 frontend for extracting formatted kernel documentation comments from C source/header files and emitting ReST, man page, none, or YAML output.

## Important APIs, Types, and Functions
`main()` builds an `argparse` interface. `MsgFormatter` capitalizes log level names to match historic output. Important options include verbosity/debug, module name, line numbers, warning controls (`-Wreturn`, `-Wshort-desc`, `-Wall`, `-Werror`), export-file filtering, output modes (`--man`, `--rst`, `--none`, `--yaml`, `--kdoc-item`), symbol selection (`--export`, `--internal`, `--symbol`, `--nosymbol`), `--no-doc-sections`, and input files.

The script imports `KernelFiles`, `RestFormat`, and `ManFormat` from `scripts/lib/python/kdoc` after version checks.

## Control Flow
`main()` parses args, expands `--wall`, configures logging, checks Python version, imports parser/output libraries, chooses output style and YAML content, instantiates `KernelFiles`, parses files, emits messages from `kfiles.msg()`, and exits 0, 1/2 via argparse/abnormal errors, or 3 when `--werror` sees warnings.

## State and Persistence
The script writes documentation output to stdout or a YAML file path via the library. It does not persist state otherwise. `WERROR_RETURN_CODE` is 3.

## Dependencies and Integration Points
Depends on Python 3.6+ for normal operation and warns below 3.7. It modifies `sys.path` to load in-tree `kdoc` libraries. It is used by kernel documentation builds and by `kernel-doc --none` checks during compilation.

## Risks and Edge Cases
For Python older than 3.6, `--none` exits 0 to avoid breaking builds, while other modes abort. Output-mode exclusivity has an exception for YAML content selection. There are visible typos in help strings, but they do not affect behavior. Library import is delayed to keep old-Python failure graceful.

## Test Signals
Run with ReST, man, none, YAML, export/internal/symbol filtering, warnings, and `--werror`. Build-system use of `kernel-doc --none` is the critical integration check.
