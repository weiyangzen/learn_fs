# sources/distributed-fs/lizardfs/src/master/restore.cc

## Purpose

`restore.cc` is the changelog replay interpreter for master/metarestore recovery. It parses textual changelog entries, dispatches them to filesystem apply functions, enforces monotonically contiguous metadata versions, and supports both strict and parse-error-tolerant restore modes. The file was read as a complete 1054-line implementation.

## Important APIs, Types, and Functions

Public functions are `restore_reset`, `restore`, and `restore_setverblevel`; `restore_line` is the central dispatcher. Parser macros `EAT`, `GETNAME`, `GETPATH`, `GETDATA`, `GETCHAR`, `GETU32`, and `GETU64` decode changelog syntax and percent-escaped data. Operation handlers include access, append, acquire, attr, checksum, create/session/free-inodes/incversion/link/length/move, lock operations, purge/release/repair, seteattr/setgoal/setpath/settrashtime/setxattr, ACL/richACL/quota, clone/symlink/undel/unlink/unlock/nextchunkid/trunc/write, and deprecated snapshot/emptytrash/emptyreserved forms.

## Control Flow

`restore` initializes expected versions from `fs_getversion`, ignores entries older than the current version, detects duplicate entries, rejects holes in changelog sequence, and otherwise calls `restore_line`. `restore_line` parses a `": timestamp|OP..."` suffix, switches by first operation character, matches operation names, and calls the handler. After a successful operation, `restore` checks that the filesystem metadata version advanced exactly one step. Parse errors can be ignored when `RestoreRigor::kIgnoreParseErrors` is selected; semantic operation errors stop processing.

## State and Persistence Behavior

Static restore state tracks `nextFsVersion`, `currentFsVersion`, `lastfn`, and verbosity. Several parsers use static growable buffers for paths, xattrs, and ACL strings. Filesystem state is mutated through `fs_*` functions with restore contexts and persistence is represented by the replayed changelog itself. Version sequencing is the main guard against missing or duplicated durable changes.

## Dependencies and Integration Points

Dependencies include LizardFS error codes, logging, protocol constants, filesystem core, snapshot, and operations APIs. This file is linked into `mfsmetarestore` and the master build paths that need changelog application, and CMake explicitly pulls it into the metarestore library with task/snapshot/setgoal/settrashtime support.

## Risks and Edge Cases

The parser is macro-heavy and manually advances raw C strings; malformed or truncated percent escapes can produce parse errors, and long names are capped at 255 bytes for `GETNAME`. Static buffers are not thread-safe. Some legacy/deprecated formats are still accepted. Correct restore depends on every `fs_*` apply path incrementing metadata version exactly once. Negative operation status and parse errors are treated differently by rigor mode. Changelog holes stop restore with inconsistency.

## Test Signals

Strong coverage requires golden changelog replay tests for every operation, version hole/duplicate/old-entry cases, parse-error rigor behavior, percent escaping and long data/path buffers, metadata-version mismatch injection, legacy format compatibility, and metarestore end-to-end tests from metadata plus changelogs.
