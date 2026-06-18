# sources/cloud-native/ostree/src/ostree/ot-editor.c

Purpose: implements the CLI editor prompt helper used by OSTree commands that need user-edited text. It chooses an editor using `OSTREE_EDITOR`, then `VISUAL`, then `EDITOR`, and falls back to `vi` unless the terminal is dumb and no editor is configured.

Important APIs/functions: `get_editor()` contains the environment-selection policy. `ot_editor_prompt()` creates a temporary file, writes the supplied input, closes the stream, invokes the editor through `/bin/sh -c`, reads UTF-8 content back with `glnx_file_get_contents_utf8_at()`, and deletes the temporary file before returning.

Control flow: editor resolution happens before any file work. The function writes the initial buffer to a `GFileIOStream`, shell-quotes the temp path, launches `GSubprocess` with inherited stdin, waits with `g_subprocess_wait_check()`, prefixes editor failures, reads final file contents, then runs cleanup in the `out:` block.

State/persistence: state is intentionally temporary. The only filesystem persistence is a `g_file_new_tmp()` file that is deleted best-effort on all exit paths. The edited content is returned as allocated memory; repository parameter is currently unused.

Dependencies/integration: depends on GLib/GIO subprocess and stream APIs, libglnx helpers, and `otutil.h`. It integrates with CLI code through `ot-editor.h` and follows git-like editor environment semantics.

Risks: launching through `/bin/sh -c` intentionally supports editor commands with arguments, so correctness relies on shell-quoting only the filename and trusting the editor environment variables. A dumb terminal without editor variables is a hard error. Temp-file deletion failures are ignored.

Test signals: no direct test is in this subset. Coverage would come from commands that call `ot_editor_prompt()` and from manual/editor-invocation tests, especially for env precedence, dumb terminal behavior, and editor failure propagation.
