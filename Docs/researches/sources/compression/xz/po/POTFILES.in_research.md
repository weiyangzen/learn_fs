<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/po/POTFILES.in -->
# sources/compression/xz/po/POTFILES.in

Purpose: gettext input manifest listing C files that contain translatable program strings.

Important APIs/types/functions: line-oriented file list for `xgettext`, covering xz frontend sources, `lzmainfo`, `tuklib_exit`, and liblzma string conversion.

Control flow: gettext tooling reads the manifest to extract `_`, `N_`, `W_`, and related message strings.

State and persistence: affects generated POT/PO catalogs, not runtime directly.

Dependencies and integration: used by gettext build/update scripts and `po/Makevars` configuration.

Risks: new translatable strings outside this manifest will be missing from catalogs. Removed files can break extraction.

Test signals: run translation update target and verify new/changed strings appear in `xz.pot`.
<!-- END_FILE_RESEARCH: sources/compression/xz/po/POTFILES.in -->
