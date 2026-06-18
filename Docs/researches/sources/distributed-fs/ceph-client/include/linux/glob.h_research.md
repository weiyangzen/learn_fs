<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/glob.h -->
# sources/distributed-fs/ceph-client/include/linux/glob.h

Purpose: Declares a pure glob-pattern matcher for kernel string matching.

Important APIs/types/functions: Exposes `bool glob_match(char const *pat, char const *str) __pure`.

Control flow: Callers pass a pattern and candidate string; implementation returns whether the string matches the glob syntax.

State and persistence behavior: No state; pure function contract implies no observable side effects.

Dependencies and integration points: Depends on bool/type definitions and compiler attributes. Used by subsystems needing lightweight pattern matching without regex.

Risks: Callers must know the exact supported glob syntax from implementation/tests; not a security boundary unless inputs and pattern semantics are validated.

Test signals: Pattern matching tests for wildcards, literals, empty strings, escaping if supported, long inputs, and repeated calls validating pure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/glob.h -->
