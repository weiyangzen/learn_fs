# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Print.java

Purpose: implements `find` output actions `-print` and `-print0`.

Important APIs and types: static `registerExpression()`, constructor with suffix, `apply()`, `isAction()`, and nested `Print0`.

Control flow: `apply()` writes `item.toString()` plus suffix to `FindOptions.out` and returns `Result.PASS`. `Print0` wraps a `Print` with null-byte suffix using `FilterExpression`.

State and persistence: stores suffix only. No filesystem mutation.

Dependencies and integration: extends `BaseExpression`; action classification prevents `Find` from auto-inserting a separate `-print` when explicitly present.

Risks: no escaping is applied; output is exactly path spelling plus newline or NUL. Null `FindOptions.out` causes failure if options were not initialized. `Print0` inherits `FilterExpression` depth behavior but does not use depth.

Test signals: cover newline and NUL output, action classification, explicit action avoiding auto-print insertion, multiple path spellings, and missing output stream failure.
