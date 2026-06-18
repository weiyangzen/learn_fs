<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/po4a/po4a.conf -->
# sources/compression/xz/po4a/po4a.conf

Purpose: po4a configuration for translated man pages.

Important APIs/types/functions: declares languages `ar de fr it ko pt_BR ro sr sv uk`, POT path `xz-man.pot`, and man-page source-to-output mappings with optional author addenda.

Control flow: `po4a` reads each `[type: man]` mapping, updates translations, and writes localized man pages under `po4a/man/$lang/`.

State and persistence: controls generated `.po`, `.pot`, and localized man page outputs.

Dependencies and integration: consumed by `po4a/update-po`; source man pages live in `src/xz`, `src/xzdec`, `src/lzmainfo`, and `src/scripts`.

Risks: adding a man page or language requires updating this file. Bad addenda or paths can prevent generation for one or more languages.

Test signals: run `po4a/update-po` and verify localized man pages are regenerated for all configured languages.
<!-- END_FILE_RESEARCH: sources/compression/xz/po4a/po4a.conf -->
