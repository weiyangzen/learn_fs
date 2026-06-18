# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/NodeFencer.java

Purpose: Parses configured fencing method specifications and tries each method in order until one fences the old active service successfully.

Important APIs and types: `NodeFencer.create(Configuration, String)`, constructor, `fence(HAServiceTarget)`, `fence(HAServiceTarget, HAServiceTarget)`, parser helpers, built-in method aliases `shell`, `sshfence`, and `powershell`, and private `FenceMethodWithArg`.

Control flow: Configuration text is split by newline, hash comments are stripped, each line is parsed as `Class(arg)` or `Class`, short aliases are resolved, classes are instantiated via reflection, and `checkArgs()` is called. During fencing, methods are attempted sequentially. If a destination target is supplied, the method is first tried on the destination before the source; source fencing is skipped if destination-side fencing fails.

State and persistence: Holds an ordered list of instantiated fencing methods and arguments. Fencing side effects are implementation-specific and external.

Dependencies and integration points: Used by `HAServiceTarget`, `FailoverController`, and `ZKFailoverController`. Depends on `FenceMethod`, `ReflectionUtils`, built-in fencers, and operator configuration.

Risks: Regex parsing is simple and arguments cannot include a closing parenthesis. Reflection allows custom code execution by configuration. Destination-first fencing semantics depend on `transitionTargetHAStatus` and script design. A false success can create split-brain.

Test signals: `TestNodeFencer` covers parsing, comments, aliases, custom classes, ordered fallback, misconfiguration, and success/failure aggregation.
