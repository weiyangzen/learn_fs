# sources/distributed-fs/eos/mgm/proc/user/Chmod.cc

## Purpose

`Chmod.cc` implements the legacy `ProcCommand::Chmod()` command for changing EOS namespace mode bits on one path or recursively over a directory tree.

## Important APIs, Types, and Functions

The sole entry point is `int ProcCommand::Chmod()`. It reads `mgm.path`, `mgm.option`, and `mgm.chmod.mode`, maps the path, validates names and access through macros, optionally enumerates targets with `gOFS->_find`, and applies `gOFS->_chmod`.

## Control Flow

After path mapping and token setup, the command requires both path and mode. Option exactly equal to `r` enables recursive `_find`; otherwise it builds a single-entry target map. It validates the mode string by formatting `strtoul(mode, 10)` back as decimal text and comparing with the original, then interprets the value as base 8 for `XrdSfsMode`. It switches to write access mode and calls `_chmod` for each found directory path, producing success or error lines.

## State and Persistence

The persistent state is the mode on each target namespace entry. Recursive `_find` determines the set of directories to update; this implementation does not iterate the per-directory file sets from `_find`, so the visible mutation loop is over map keys.

## Dependencies and Integration Points

It integrates with EOS path mapping, illegal-name and access-bounce macros, recursive stall accounting, and `gOFS->_chmod`. It uses legacy opaque request fields and response buffers.

## Risks and Test Signals

Mode validation is subtle: the input must look like decimal digits, but is later parsed as octal, so strings like `755` pass and become octal `0755`; invalid octal digits may pass the decimal check and then be parsed by `strtoul(..., 8)` up to the invalid character. Non-root success output prepends `2` before the printed mode, matching EOS behavior but worth regression coverage. Test signals include empty mode/path, recursive and non-recursive updates, invalid mode strings, invalid octal digits, access denial, and partial recursive failures.
