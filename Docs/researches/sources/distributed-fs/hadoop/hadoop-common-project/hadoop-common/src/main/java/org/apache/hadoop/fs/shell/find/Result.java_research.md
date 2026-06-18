# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/find/Result.java

Purpose: immutable-like value object representing expression success and whether traversal should descend further.

Important APIs and types: constants `PASS`, `FAIL`, `STOP`; `isDescend()`, `isPass()`, `combine()`, `negate()`, `toString()`, `hashCode()`, and `equals()`.

Control flow: expressions return one of the predefined constants or combined/negated instances. `combine()` ANDs pass and descend bits. `negate()` flips pass while preserving descend.

State and persistence: private booleans `success` and `descend`; no external mutation API, though fields are not final.

Dependencies and integration: used by all `find` expressions and by `Find.applyItem()` to decide stop-path recording.

Risks: only equality with `Result.STOP` is explicitly checked in `Find`, so a combined result with pass=true/descend=false equals STOP and works, but any fail+descend=false result will not be recorded as stop. Non-final fields reduce immutability clarity.

Test signals: cover constants, combine truth table, negate semantics, equality/hash, string form, and integration with stop traversal.
