# sources/distributed-fs/glusterfs/xlators/cluster/dht/Makefile.am

## Purpose
This top-level DHT automake file delegates the DHT cluster translator build to the `src` subdirectory. Its complete contents are `SUBDIRS = src`, with no trailing newline in the checked file.

## Important APIs, Types, And Functions
There are no C APIs, types, functions, or build targets defined here. The only automake variable is `SUBDIRS`, which tells automake recursion to descend into `xlators/cluster/dht/src`.

## Control Flow
During an autotools build, automake processes this directory and recurses into `src` for actual target definitions. Installation, library target creation, headers, compiler flags, and unit-test conditionals are all owned by `src/Makefile.am`, not by this file.

## State And Persistence
The file has no runtime state and no generated persistent artifacts by itself. Its build-system effect is persistent only through the generated `Makefile.in`/`Makefile` recursion graph: excluding `src` here would prevent DHT translator modules from being built under this directory.

## Dependencies And Integration Points
It depends on the repository's autotools recursion model. The integration point is the child `sources/distributed-fs/glusterfs/xlators/cluster/dht/src/Makefile.am`, which defines `dht.la`, `nufa.la`, and `switch.la`.

## Risks
The main risk is accidental deletion or change of the `SUBDIRS` assignment, which would silently remove DHT translator build coverage from recursive builds. The lack of a trailing newline may trigger style or packaging warnings in some tooling, though automake can still parse the assignment.

## Test Signals
Run autoreconf/configure or the project's normal autotools build and verify that `xlators/cluster/dht/src` is entered and the DHT modules are produced. Static checks can simply assert this file contains exactly the intended `SUBDIRS = src` delegation.
