# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/FileUtil.m

Purpose: implements the legacy Authorization Services file operation wrapper.

Important APIs and control flow: each method builds a null-terminated argv array and calls `[[AuthUtil shared] execUnixCommand:args:output:nil]` for `/bin/mv`, `/bin/cp`, `/usr/sbin/chown`, or `/bin/rm`. `autorizedChown:` constructs `owner:group` dynamically.

State and persistence: no local persistent state. Effects are direct filesystem mutations performed with elevated privileges.

Dependencies and integration: used by `PListManager krb5TiketAtLoginTime:` when modifying `/etc/authorization`. It uses `AuthUtil`'s deprecated privileged execution path instead of the safer XPC helper.

Risks: arbitrary source/destination paths are accepted. No `--` delimiter is used before paths, so paths beginning with `-` can be interpreted as options. There is no atomic write protocol beyond what callers implement. Error propagation is only an `OSStatus`.

Test signals: move/copy/chown/delete success and denial, path option-injection cases, nonexistent source/destination, ownership failure, and preserving backups around `/etc/authorization`.
