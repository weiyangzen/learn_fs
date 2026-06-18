<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/markdownlint-tab-spacing.js -->
# sources/control-plane/rook/tests/scripts/markdownlint-tab-spacing.js

Purpose: custom markdownlint rule enforcing indentation to exact four-space boundaries outside fenced code blocks.

Important APIs and control flow: exports rule `strict-tab-spacing`. It tracks fenced code block depth, counts leading spaces, and reports/fixes lines whose indentation is not divisible by four. It tries to infer whether to round down or up based on a two-space cutoff.

State, persistence, and integration: no persistent state; CI/docs lint tooling reads it. Dependencies include markdownlint custom rule contracts. Risks include implicit globals, simplistic code-fence tracking, and a likely fix calculation issue where `generateTabSpaces(floor)` treats the quotient as a raw space count instead of multiplying by four. Test signals are lint failures and generated fix information.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/markdownlint-tab-spacing.js -->
