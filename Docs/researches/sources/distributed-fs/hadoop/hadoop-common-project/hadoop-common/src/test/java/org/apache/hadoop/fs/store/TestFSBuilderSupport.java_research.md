# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/store/TestFSBuilderSupport.java

Purpose: Tests `FSBuilderSupport` option parsing and default `FSBuilder` interface compatibility, especially numeric forwarding from float/double options to long getters.

Important APIs/types/functions: `FSBuilder`, `FSBuilderSupport`, builder default methods `opt`/`must` for numeric and boolean types, `getLong`, `getPositiveLong`, `Configuration.getBoolean`, and inner `SimpleBuilder`/`BuilderImpl`.

Control flow: Tests build a minimal `BuilderImpl` backed by `Configuration(false)`. Float/double `opt` and `must` values are stored through default interface methods and read as longs (`1.8f` -> `1`, `2.0e3` -> `2000`). Long options are read unchanged. String values that look like floats or huge doubles fall back to the provided default. Negative longs are returned by `getLong` but rejected by `getPositiveLong` in favor of default. Boolean options verify stored true/false values and that a non-boolean string is handled by `Configuration`.

State/persistence: Each builder holds an in-memory `Configuration`. No filesystem state.

Dependencies/integration: Protects `FSBuilder` binary/source compatibility for external implementations by using a minimal implementation that relies on interface defaults.

Risks: Numeric conversion truncates floating values; this is intentional but compatibility-sensitive. The comment references downstream compatibility (HBase), so adding new abstract methods to `FSBuilder` would break compilation here.

Test signals: Exact parsed long/default values, positive-long fallback for negatives, boolean option reads, and compile-time enforcement of minimal builder compatibility.
