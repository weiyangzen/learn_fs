## sources/distributed-fs/openafs/src/rxgen/rpc_util.c

### Purpose
`rpc_util.c` provides shared rxgen process state, list utilities, type-formatting helpers, diagnostics, cleanup-on-failure, and token expectation messages.

### Important APIs, Types, And Functions
Public functions include `reinitialize`, `streq`, `findval`, `storeval`, `fixtype`, `stringfix`, `ptype`, `isvectordef`, `pvname`, `error`, `crash`, `record_open`, `expected1` through `expected4`, and `tabify`. Static helpers implement typedef chasing, lowercasing, token-to-string mapping, and source caret printing.

### Control Flow
`reinitialize()` clears scanner buffers and parser globals before a generation run. `fixtype()` follows typedef aliases for vector element handling. `error()` prints the current source line and caret, reports filename and line, then calls `crash()`, which unlinks recorded output files and exits.

### State, Persistence, And Dependencies
The file owns `curline`, `where`, `linenum`, `infilename`, `outfiles`, `nfiles`, `fout`, `fin`, and `defined`. It mutates parser globals declared in `rpc_parse.c`. Output filenames recorded by `record_open()` persist only so failed generation can unlink partial files.

### Integration Points
All rxgen modules include these helpers via `rpc_util.h`. The scanner uses source-position globals and `expected*` diagnostics; the parser and emitters use type printing and definition lookup.

### Risks
The cleanup list is capped at six files. `error()` calls `crash()` twice, though the first exits. Fixed buffers for diagnostics and lowercased names can overflow if future token strings or names grow. `isvectordef()` is structured as an infinite loop with immediate returns and depends on valid `relation` values.

### Test Signals
Signals include parser error fixtures verifying caret placement and cleanup, typedef/vector formatting cases, repeated generation runs through `reinitialize()`, output-file count limits, and `scan_print` suppression behavior.
