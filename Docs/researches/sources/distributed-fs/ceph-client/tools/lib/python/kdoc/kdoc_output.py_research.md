<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_output.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_output.py

## Purpose
This module formats parsed kernel-doc `KdocItem` objects into ReST or man/troff output. It defines a filtering base class and concrete output styles for Sphinx documentation and man pages.

## Important APIs, Types, and Functions
- Module-level `KernRe` regexes detect kernel-doc inline markup for constants, functions, parameters, environment variables, enum/struct/typedef/union references, members, and function pointers.
- `OutputFormat` defines output modes (`OUTPUT_ALL`, `OUTPUT_INCLUDE`, `OUTPUT_EXPORTED`, `OUTPUT_INTERNAL`), filter state, warning dispatch, `check_doc`, `check_declaration`, `msg`, and `output_symbols`. Virtual `out_*` methods are overridden by subclasses.
- `RestFormat` converts docs into ReST directives such as `.. c:function::`, `.. c:enum::`, `.. c:macro::`, `.. c:type::`, and `.. c:struct::`. It highlights inline references, preserves literal/code blocks, emits optional line markers, and formats parameters, members, sections, defaults, and definitions.
- `ManFormat` emits troff man pages with `.TH`, `.SH`, `.IP`, `.BI`, `.TS`, and formatting escapes. It handles dates from `KBUILD_BUILD_TIMESTAMP`, module names, SEE ALSO tails, grid/simple table conversion, code blocks, lists, functions, enums, vars, typedefs, structs, and doc sections.

## Control Flow and State
Formatting is item-driven. `set_filter` configures which symbols are eligible. `output_symbols` calls `set_symbols`, then dispatches each item through `msg`. `RestFormat` accumulates output in `self.data` with a mutable `lineprefix`. `ManFormat.msg` calls the base dispatch then appends a tail for every emitted page. Both subclasses transform inline markup through ordered regex substitutions before writing output.

## Dependencies and Integration Points
It depends on `KernelDoc` constants, `type_param`, and `KernRe`. `KernelFiles` instantiates an output style and calls `output_symbols`. The output is intended for kernel documentation builds and man-page generation.

## Risks and Test Signals
Filtering behavior is shared across both formats, so mode bugs affect all output. ReST highlighting must avoid mutating literal blocks; man highlighting must escape leading dots and translate tables/code/list constructs correctly. `ManFormat.msg` appends a SEE ALSO tail even if base dispatch produced empty data, which may need care for filtered items. Some local variables such as `module` are assigned but unused. Tests should cover every `KdocItem` type, filters, no-symbol exclusions, line numbers, literal/code blocks, table conversion, function-pointer signatures, missing descriptions, and timestamp formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_output.py -->
