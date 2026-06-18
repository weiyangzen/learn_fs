<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/objdiff -->
# sources/distributed-fs/ceph-client/scripts/objdiff

## Purpose

`objdiff` compares the generated assembly of a single object between two source trees or build outputs. It helps diagnose compiler/codegen changes at object granularity.

## Important APIs, Types, and Functions

Functions are `usage()`, `get_output_dir()`, `do_objdump()`, `dorecord()`, `dodiff()`, and `doclean()`. Actions include recording objdump output, diffing current output against a saved baseline, and cleaning generated files.

## Control Flow

The script parses an action and object path, determines output paths, runs objdump with a stable set of disassembly/source options, stores baseline output for `record`, produces a unified diff for `diff`, or removes saved output for `clean`.

## State and Persistence Behavior

It persists objdump text under an output directory derived from the object path. Diff action reads that baseline and writes diff output to stdout.

## Dependencies and Integration Points

It depends on shell, objdump, diff, mkdir/rm, and Kbuild object paths. It is a developer diagnostic helper rather than a production build step.

## Risks and Edge Cases

Objdump output includes paths, addresses, debug/source context, and tool-version formatting that can create noisy diffs. Missing debug info or stripped objects reduce usefulness. Cross-toolchain comparisons require the right objdump.

## Test Signals

Record and diff an unchanged object, a changed object, a missing object, and a cross-compiled object. Confirm clean removes only its own generated baseline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/objdiff -->
