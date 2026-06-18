# sources/distributed-fs/ceph-client/Documentation/sphinx/automarkup.py

Purpose: this Sphinx extension performs kernel-specific automatic markup after doctree resolution. It converts plain text references to functions, C types, Documentation files, ABI symbols/files, and kernel commits into cross-reference nodes where possible.

Important APIs, types, and functions: regexes detect `function()`, `struct/union/enum/typedef` names, `Documentation/*.rst|txt`, ABI file paths, ABI symbols under `/sys`, `/config`, or `/proc`, C namespaces, and commit hashes. `markup_refs()` collects regex matches, sorts by source position, and emits replacement docutils nodes. `markup_func_ref_sphinx3()` and `markup_c_ref()` resolve C-domain references with namespace fallback. `markup_doc_ref()` and `markup_abi_ref()` resolve std doc/ref links. `add_and_resolve_xref()` constructs `pending_xref` and asks the domain to resolve it. `markup_git()` creates git.kernel.org commit links. `auto_markup()` walks paragraph text nodes while avoiding literals and existing references. `setup()` connects `doctree-resolved`.

Control flow: for each paragraph text node, the extension finds all possible references, emits normal text before each match, replaces matched text with either resolved references, broken-xref literal nodes, or original text, then updates the parent node.

State and persistence: global `failed_lookups` caches failed function targets; global `c_namespace` is updated per document. No disk state is written. ABI lookup is delegated to `kernel_abi.get_kernel_abi()`.

Dependencies and integration: depends on docutils nodes, Sphinx domains, `kernel_abi`, the C domain object inventory, and the builder's ability to resolve references. It is integrated through the Sphinx event system.

Risks: overlapping regex matches are not explicitly filtered; sorted matches can produce duplicated or out-of-order replacement text if patterns overlap in future cases. Global state can interact with parallel builds, though the extension declares parallel safe. Failed lookup caching may hide later targets added in the same build. Test signals include Sphinx builds with representative function/type/doc/ABI/commit text, literal/reference exclusion checks, namespace-specific C references, LaTeX builder behavior, and parallel build runs.
