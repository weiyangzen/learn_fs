<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/filter.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/filter.go

Purpose: implements a user-facing file filter DSL that compiles to an `expr` program over filesystem stat metadata.

Important APIs/types/functions: `FileInfo`, `FileInfoFilter`, `CompileFilter`, `preprocessDSL`, `setFileType`, `normalizeOctal`, `StatToFileInfo`, `ago`, `parseExtendedDuration`, `parseBytes`, `globMatch`, `regexMatch`, `ApplyFilter`, and `ApplyFilterByStatT`.

Control flow: `CompileFilter` preprocesses DSL text by normalizing octal mode/permission literals, expanding `type == ...` into bitmask expressions, rewriting age comparisons into `ago(...)`, wrapping size units in `bytes(...)`, and mapping lower-case identifiers to exported `FileInfo` fields. It compiles with helper functions, then returns a runtime filter that enforces boolean results. `ApplyFilter` obtains `Lstat`, converts `syscall.Stat_t`, and evaluates the filter.

State and persistence: no persistence; compiled expression objects are captured by returned closures. `now`/`ago` use current wall time at evaluation.

Dependencies and integration points: depends on `expr-lang/expr`, regex/path helpers, and provider `Lstat`. Integrated into `StreamPathsLexicographically` to filter walked paths.

Risks: regex preprocessing is complex and order-sensitive. `sizeRe` includes `=` but not `==`, so unit handling around equality depends on `expr` syntax after rewrite. `parseExtendedDuration` indexes the last byte without guarding empty strings, though regex normally prevents empty duration. `ApplyFilter` is Linux-specific due to `syscall.Stat_t`.

Test signals: `filter_test.go` covers valid expressions, type expressions, invalid type syntax, invalid expressions, time/size units, and preprocessing rewrites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/filter.go -->
