# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/xforms_lists.py

Purpose: Defines parser transformations that normalize kernel C declarations before kernel-doc parsing, removing attributes and rewriting common declaration macros into C-like declarations.

Important APIs/types/functions: `CTransforms` contains `struct_xforms`, `function_xforms`, `var_xforms`, and `xforms`. `apply(xforms_type, source)` runs the appropriate transformation sequence over a string or `CTokenizer`.

Control flow: The transform lists are ordered. `CMatch` substitutions run token-aware rewrites for common kernel macros/attributes; `KernRe` entries force conversion to string and apply plain regex replacements. `apply()` returns the transformed source string or the original source for unknown transform classes.

State and persistence: Class-level transformation tables are static. No per-instance persistent state beyond the instance itself.

Dependencies/integration: Depends on `kdoc.kdoc_re.KernRe` and `kdoc.c_lex.CMatch`/`CTokenizer`. It is injected into `KernelDoc` and used by `dump_struct()`, `dump_function()`, and `dump_var()`.

Risks: Ordering is semantically important; placing string regex transforms too early loses tokenizer advantages. Macro rewrites are necessarily incomplete and must track kernel declaration patterns. `CMatch` capture numbering must match replacement strings; changes in tokenizer behavior can break many parser cases. Attribute removal can hide meaningful type information if a new macro is not just annotation.

Test signals: Fixture declarations should cover cacheline/alignment attributes, bitmap/kfifo/hashtable/flex-array macros, struct_group variants, syscall/function annotations, `LIST_HEAD`, comments, and `_noprof` name normalization.
