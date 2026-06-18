# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/__init__.py

Purpose: Defines shared generator infrastructure for the XDR-to-C code generator.

Important APIs and functions: `create_jinja2_environment(language, xdr_type)` locates templates and installs globals (`annotate`, `public_apis`, `pass_by_reference`, `structs`). `get_jinja2_template` loads typed templates. `find_xdr_program_name`, `header_guard_infix`, and `kernel_c_type` provide naming and C type mapping. `Boilerplate` and `SourceGenerator` are abstract base classes for concrete emitters.

Control flow: Language selection currently supports only `C`; unsupported languages raise `NotImplementedError`. Concrete generators instantiate environments and render templates to stdout.

State and persistence behavior: No file writes here. It reads template files via Jinja2 and observes global AST/parser side-channel state.

Dependencies and integration points: Used by every generator module and by subcommands. Depends on Jinja2, pathlib, `xdr_ast`, and `xdr_parse`.

Risks: Imports are absolute/top-level, so execution path must include the xdrgen directory. The environment reads global state at creation; repeated parses in one process can inherit stale AST globals unless reset externally.

Test signals: Instantiate environments for each xdr type, render known templates, verify type mapping for builtins and defined types, and assert unsupported languages fail.
