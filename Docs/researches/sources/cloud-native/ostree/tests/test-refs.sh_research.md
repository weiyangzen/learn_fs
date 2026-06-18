# sources/cloud-native/ostree/tests/test-refs.sh

## Purpose
This test covers the core `ostree refs` CLI: sorted listing, prefix filtering, revision output, deletion, creation, validation, local versus remote namespace handling, hidden file filtering, and alias symlink refs.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1`, `ostree commit`, `ostree refs`, `--list`, `--revision`, `--delete`, `--create`, `--force`, `-A` alias mode, `ostree rev-parse`, `ostree summary -u`, and fixture assertion helpers.

## Control Flow
The test commits refs under flat and nested names, checks sorted output and prefix behavior, verifies revision-paired listing, exercises safe no-op and explicit deletion, validates `--create` failure modes and forced replacement, ignores hidden `.spooky` files in ref directories, rejects invalid ref names, accepts names with `._-`, checks cleanup after failed creates, tests reuse of deleted directories, distinguishes remote-style `origin:` refs from local refs, and then creates alias symlinks from stable refs to versioned refs. It verifies alias resolution follows updated targets, alias swapping works, deletion of a target with aliases is rejected, and aliases to remote or nonexistent refs fail.

## State And Persistence
Persistent state includes `repo/refs/heads`, nested ref directories, remote-style refs, alias symlinks, summary output, and commits used to update target revisions. Hidden files are manually inserted to simulate external tooling artifacts.

## Dependencies And Integration Points
This integrates ref validation, filesystem-backed ref layout, symlink alias support, summary generation, revision resolution, and remote namespace parsing. It also depends on shell brace expansion and UTF-8 filesystem support for the hidden marker file.

## Risks
Ref operations can accidentally treat directories as refs, leave temp files after failed creation, overwrite prefixes, expose hidden files, allow invalid names, or break aliases after target updates. Alias deletion semantics guard against dangling stable refs.

## Test Signals
Seven TAP results cover hidden refs, invalid refs, valid character refs, general ref operations, symlink refs, remote alias rejection, and broken alias rejection. Failures are usually visible as count mismatches, unexpected `rev-parse` results, or expected stderr text not appearing.
