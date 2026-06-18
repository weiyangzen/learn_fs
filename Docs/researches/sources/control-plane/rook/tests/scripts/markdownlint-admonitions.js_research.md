<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/markdownlint-admonitions.js -->
# sources/control-plane/rook/tests/scripts/markdownlint-admonitions.js

Purpose: custom markdownlint rule enforcing MkDocs admonition formatting. It ensures admonition body text immediately follows the header and is indented four spaces beyond the header indent.

Important APIs and control flow: exports a markdownlint rule named `mkdocs-admonitions` with parser `none`. It iterates lines, detects headers starting with `!!!` after left trim, computes expected body indentation, reports an error and deletion fix for blank body lines, or a replacement indentation fix for incorrectly indented body lines.

State, persistence, and integration: no persistent state; markdownlint consumes it during docs checks. Dependencies include markdownlint's custom rule API. Risks include implicit global variables (`start_spaces`, `got_tab_spaces`), failure if the admonition header is the final line, and only checking the first body line. Test signals are markdownlint errors with autofix metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/markdownlint-admonitions.js -->
