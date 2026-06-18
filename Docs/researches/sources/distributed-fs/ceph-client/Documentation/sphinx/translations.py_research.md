<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/translations.py -->
# sources/distributed-fs/ceph-client/Documentation/sphinx/translations.py

## Purpose
Sphinx extension that inserts a language selector into each document and renders it for HTML output when translations of the current page exist and resolve.

## Important APIs, Types, And Functions
- `all_languages` maps language codes, including `None` for English, to display names.
- `LanguagesNode` is a placeholder docutils element.
- `TranslationsTransform` creates pending document cross references for alternate language paths.
- `process_languages()` replaces resolved language links with rendered `translations.html` template output.

## Control Flow
The transform runs late (`default_priority = 900`), derives the current language from document names under `translations/<lang>/...`, normalizes translated documents back to their English source path, and inserts a `LanguagesNode` at the top of the document. During `doctree-resolved`, unresolved pending refs have become plain text, so `process_languages()` filters only `nodes.reference` children and renders the HTML selector.

## State And Persistence
No persistent state is written. The only durable effect is the inserted raw HTML in the resolved doctree for HTML builders. Non-HTML builders remove the placeholder node.

## Dependencies And Integration Points
Depends on Sphinx standard-document references, docutils transforms, the HTML template `translations.html`, and the repository convention that translations live below `translations/<lang_code>/`.

## Risks And Edge Cases
Language availability is inferred through reference resolution rather than a manifest, so broken translation paths silently disappear from the selector. The Spanish code is `sp_SP`, which may need consistency with repository naming. The extension assumes `docname` path separators match `os.sep`.

## Test Signals
Build HTML for English and translated documents, verify current-language display, only existing translations linked, non-HTML builders omit the node, and pages under `translations/<lang>/` link back to English plus other available translations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/translations.py -->
