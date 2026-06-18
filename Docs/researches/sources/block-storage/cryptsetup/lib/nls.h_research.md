# File Research: sources/block-storage/cryptsetup/lib/nls.h

This header centralizes native language support macros.

Behavior:
- Defines default `LOCALEDIR` as `/usr/share/locale` if not provided.
- Includes `<locale.h>` when `HAVE_LOCALE_H` is set; otherwise stubs `setlocale`.
- When `ENABLE_NLS` is set, includes `<libintl.h>` and maps:
  - `_()` to `gettext()`
  - `N_()` to `gettext_noop()` if available, otherwise identity
- When NLS is disabled, stubs `bindtextdomain()` and `textdomain()`, maps `_()` and `N_()` to identity, and defines `ngettext()` as a singular/plural conditional.

This header is why source files such as `luks2_reencrypt.c` and `random.c` can use `_()` around user-visible log messages without conditional localization logic in each file.
