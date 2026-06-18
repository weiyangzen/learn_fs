# sources/distributed-fs/ceph-client/scripts/remove-stale-files

Purpose: `remove-stale-files` is a Kbuild startup cleanup script for generated files that were moved, renamed, or removed from the build but may still be present in developer trees after git updates or bisects.

Important APIs, types, and functions: it is a shell script with `set -e` and a small fixed list of `rm -f` commands. Current removals include the old `scripts/selinux/genheaders/genheaders`, top-level `*.spec`, and `lib/test_fortify.log`.

Control flow: it runs unconditionally and exits on unexpected command failure, though `rm -f` makes the intended cleanup idempotent.

State and persistence: it deletes stale files from the working tree. There is no record of what was removed and no user prompt.

Dependencies and integration points: Kbuild invokes this before building so stale generated artifacts do not mask source moves or create confusing untracked files.

Risks: every path added to this script must be known generated output; adding source-like paths would silently delete user files. Because it is intentionally temporary, stale entries should be removed after enough release cycles.

Test signals: run in clean and dirty trees with/without listed artifacts, verify idempotence and absence of build-visible stale files. Git status after cleanup is a practical signal.
