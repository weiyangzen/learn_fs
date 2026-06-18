<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/po4a/update-po -->
# sources/compression/xz/po4a/update-po

Purpose: updates translated man-page POT/PO files and regenerates localized man pages.

Important APIs/types/functions: checks for `po4a`, locates `po4a.conf`, derives `PACKAGE_VERSION`, creates temporary `*.po.authors` addenda from translator comments, invokes `po4a` with diff-friendly options, post-processes tables with Perl, and rewrites `xz-man.pot` header.

Control flow: validate tool/config, generate author addenda for each `.po`, run `po4a --force`, remove addenda, insert `\&` after non-ASCII table chars, then replace POT header from `po/xz.pot-header`.

State and persistence: modifies `.po`, `xz-man.pot`, and `man/*/*.1`; temporary `.po.authors` files are removed.

Dependencies and integration: depends on `/bin/sh`, po4a, perl, sed, and `build-aux/version.sh`.

Risks: in-place Perl editing touches generated man pages broadly. The script exits if po4a is missing, which is acceptable for update workflow but not for ordinary builds.

Test signals: run from `po4a/`, inspect git diff for expected POT version/header changes and valid localized man pages.
<!-- END_FILE_RESEARCH: sources/compression/xz/po4a/update-po -->
