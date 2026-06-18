# sources/cloud-native/ostree/git.mk

Purpose: imported Makefile helper that auto-generates `.gitignore` files for autotools projects from build metadata rather than maintaining ignores manually.

Important APIs/functions: variables `GIT_MK_URL`, `GITIGNORE_MAINTAINERCLEANFILES_TOPLEVEL`, `GITIGNORE_MAINTAINERCLEANFILES_MAKEFILE_IN`, `GITIGNORE_MAINTAINERCLEANFILES_M4_LIBTOOL`; targets `git-all`, `git-mk-install`, `git-mk-update`, `.gitignore`, `all`, `gitignore`, recursion targets, `maintainer-clean`, and `gitignore-clean`.

Control flow: `git-mk-install` finds `Makefile.am` files and appends `-include $(top_srcdir)/git.mk` when absent. The `.gitignore` rule inspects automake variables and autoconf traces to emit generated files for gtk-doc, translated docs, gsettings, appdata/appstream, po, configure/libtool, dejagnu, libtool objects, tests, programs, clean files, Vala outputs, backups, and object/dependency dirs. Output is sorted/uniqued and moved atomically.

State and persistence: writes `.gitignore` files and may edit every `Makefile.am` during install. `gitignore-clean` removes generated ignore files. It does not belong in release tarballs according to comments.

Dependencies and integration: integrates GNU make, automake variables, autoconf tracing, gtk-doc/yelp/gettext conventions, libtool, and project `Makefile.am` include patterns.

Risks and test signals: risks include imported upstream drift, generated ignore omissions for newer tools, command substitution portability, and broad `Makefile.am` edits. Signals are clean `git status` after build/clean cycles and generated `.gitignore` contents matching build artifacts.
