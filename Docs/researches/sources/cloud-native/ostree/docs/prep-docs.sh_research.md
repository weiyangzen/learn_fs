# sources/cloud-native/ostree/docs/prep-docs.sh

Purpose: stages generated API and man-page HTML into the Jekyll docs directory before site generation.

Important APIs/functions: `docsdir=$(dirname "$0")`, `topdir="$docsdir/.."`, source dirs `apidoc/html` and `man/html`, destination dirs `docs/reference` and `docs/man`, plus `rm -rf` and `cp -r`.

Control flow: strict shell mode. It first verifies gtk-doc API HTML exists, otherwise tells the user to rebuild with `--enable-gtk-doc`; then replaces `docs/reference`. It then verifies man HTML exists, otherwise tells the user to rebuild with `--enable-man` and `make manhtml`; then replaces `docs/man`.

State and persistence: destructively refreshes `docs/reference` and `docs/man` with generated content. No incremental merge is attempted.

Dependencies and integration: consumes outputs from autotools/gtk-doc/man generation and feeds `_config.yml` include paths for Jekyll/GitHub Pages.

Risks and test signals: risks include unquoted paths in some variables, destructive deletion of destination dirs, stale generated docs if upstream build was not refreshed, and missing tooling. Signals are successful script run followed by Jekyll rendering of API and man references.
