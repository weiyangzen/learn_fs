<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/filter_test.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/filter_test.go

Purpose: unit tests for the filesystem filter DSL.

Important APIs/types/functions: `TestCompileFilter_ValidExpressions`, `TestCompileFilter_TypeExpressions`, `TestCompileFilter_InvalidTypeExpressions`, `TestCompileFilter_InvalidExpression`, `TestCompileFilter_TimeAndSizeUnits`, and `TestPreprocessDSL_Rewrites`.

Control flow: tests compile DSL expressions, run them against synthetic `FileInfo` values, and compare booleans. Type tests vary raw mode bits. Rewrite tests inspect preprocessed output substrings.

State and persistence: no persistence; time-based tests use `time.Now()` and relative timestamps.

Dependencies and integration points: depends on `testify/assert/require`; validates filter behavior used by path streaming.

Risks: time tests can be sensitive near exact thresholds, though chosen offsets are broad. Tests do not cover `ApplyFilter` with real `syscall.Stat_t`, empty strings in helper parsers, or all invalid unit combinations.

Test signals: broad signal for DSL correctness and regression protection around octal/type/time/size rewrites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/filter_test.go -->
