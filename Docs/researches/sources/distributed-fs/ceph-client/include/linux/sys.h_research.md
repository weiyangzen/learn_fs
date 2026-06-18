<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys.h -->
# sources/distributed-fs/ceph-client/include/linux/sys.h

## Purpose

`sys.h` is a legacy placeholder header. Its comments state it is no longer used or needed, retaining only disabled historical syscall alias notes.

## Important APIs, types, and functions

There are no active exported APIs. A `#ifdef notdef` block documents obsolete syscall aliases such as old wait, uname, stat, signal, and signal-mask variants, but they are not compiled.

## Control flow

There is no runtime or compile-time control flow beyond the include guard and inactive block.

## State and persistence behavior

No state exists.

## Dependencies and integration points

It has no includes and should not be a dependency for new code. Its only integration value is preserving a historical include path.

## Risks and test signals

Risk is accidental reliance by new code on an empty legacy header or re-enabling obsolete aliases. Tests are limited to compile checks that removing includes from consumers has no effect and that no active symbols are expected from this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys.h -->
