# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-annotations/src/main/java/org/apache/hadoop/classification/tools/StabilityOptions.java

Purpose: option parsing and normalization helper for Hadoop doclets' API stability filters.

Important APIs, types, and functions: constants are `-stable`, `-evolving`, and `-unstable`. `Level` orders `STABLE`, `EVOLVING`, and `UNSTABLE`; `level` is a volatile static defaulting to `UNSTABLE`. `optionLength()` identifies supported options. `setFromOptionName()` promotes the current level to the least restrictive requested level. `applyToRootProcessor()` maps the selected level to `RootDocProcessor.setStability()`. `validOptions()` scans doclet option arrays, and `filterOptions()` removes Hadoop stability flags before passing options to delegate doclets.

Control flow: doclet wrappers call `validOptions()` or custom `Option.process()` during option parsing, then call `applyToRootProcessor()` before processing the doclet environment.

State and persistence: global JVM state is `level`; there is no persistence. The volatile field provides visibility but not full reset semantics between independent doclet runs.

Dependencies and integration points: depends on `Reporter` and Java collections. Integrates with `RootDocProcessor`, JDiff wrappers, and StandardDoclet wrappers.

Risks and test signals: because `setFromOptionName()` only updates when `next.ordinal() > level.ordinal()` and the default is already `UNSTABLE`, command-line `-stable` or `-evolving` cannot make the filter stricter through that path unless `level` was reset lower first. This is a likely semantic bug. Test signals should cover all option combinations and sequential invocations in one JVM.
