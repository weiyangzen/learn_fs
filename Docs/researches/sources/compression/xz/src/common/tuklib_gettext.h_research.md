<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_gettext.h -->
# sources/compression/xz/src/common/tuklib_gettext.h

Purpose: gettext wrapper that provides localization macros with or without NLS.

Important APIs/types/functions: `TUKLIB_GETTEXT`, `tuklib_gettext_init`, `_`, `ngettext`, `N_`, and `W_`.

Control flow: if NLS is enabled, include `libintl.h`, set locale, bind text domain, and use gettext. Otherwise still set locale but map translations to original strings.

State and persistence: initializes process locale and gettext text domain; no file writes.

Dependencies and integration: used by xz frontend and tuklib modules; `W_` coordinates with xgettext options for word-wrapped strings.

Risks: locale initialization is process-global. Disabled NLS still depends on locale for multibyte handling.

Test signals: run tools under translated locale and under `--disable-nls`; verify plural handling and word-wrap comments extraction.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_gettext.h -->
