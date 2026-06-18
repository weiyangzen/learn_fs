# sources/distributed-fs/openafs/src/external/import-external-git.pl

## Purpose
Automates importing selected files from an external git repository into `src/external/<module>` in the OpenAFS tree, recording the imported commit and creating an OpenAFS commit that describes upstream changes.

## Important APIs, Types, And Functions
This Perl script uses `Getopt::Long`, `File::Basename`, `File::Temp`, `File::Path`, `IO::File`, `IO::Pipe`, `Pod::Usage`, and `Cwd`. Inputs are `<module> <repository> [<commitish>]`, plus `--externalDir` and `--nofixwhitespace`. State files include `<module>-files`, `<module>-last`, and optional `<module>-author`.

## Control Flow
It reads source-to-destination mappings, reads the previous imported commit and author override, archives selected files from the external repo into a temporary tree, stashes local changes in the module directory, copies mapped files into place, adds new files, removes committed files no longer mapped, writes `<module>-last`, builds a commit message with upstream shortlog and file lists, commits, optionally rebases with whitespace fixing, and amends to trigger hooks. On failure it resets hard to `HEAD` and later pops any stash.

## State And Persistence
The script mutates the OpenAFS git working tree, index, commits, module directory contents, and `<module>-last`. It may stash and pop pre-existing local changes.

## Dependencies And Integration Points
It integrates external upstream source snapshots into OpenAFS vendored directories and depends heavily on command-line git, tar, cp, and module mapping files.

## Risks And Test Signals
The script uses shell string interpolation for paths and file lists, so spaces or metacharacters in names are risky. Error recovery uses destructive `git reset --hard HEAD` inside the module directory. Tests should use disposable repos to cover added/deleted files, mapping parse errors, missing files, author override, no-change imports, dirty-tree stash/pop, whitespace-fix failures, and commit-message content.
