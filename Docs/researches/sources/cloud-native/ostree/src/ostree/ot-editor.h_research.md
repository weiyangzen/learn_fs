# sources/cloud-native/ostree/src/ostree/ot-editor.h

Purpose: declares the editor prompt interface for OSTree CLI code.

Important APIs/types/functions: includes `<gio/gio.h>` and `ostree.h`, then exports `char *ot_editor_prompt(OstreeRepo *repo, const char *input, GCancellable *cancellable, GError **error)`.

Control flow/state: this header has no executable flow or persistent state. Its contract is transfer-full string ownership on success and GLib-style error reporting on failure.

Dependencies/integration: the signature accepts `OstreeRepo *` for command integration even though the current implementation does not use it. Consumers must link `ot-editor.c`.

Risks: callers must free the returned string and handle `NULL` with `GError`. The unused repo parameter can mislead readers into expecting repository-scoped temp files.

Test signals: compile/link coverage is the main signal; behavioral coverage lives in callers of `ot_editor_prompt()`.
