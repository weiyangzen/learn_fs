# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/Makefile.am

Purpose: top-level Automake fragment for the `performance/nl-cache` translator. It delegates all build work to `src`.

Important APIs, types, and functions: declares `SUBDIRS = src` and an empty `CLEANFILES`. There are no runtime APIs or C symbols in this file.

Control flow: during recursive Automake builds, the parent performance tree enters this directory and then descends into `src/Makefile.am`, where the actual `nl-cache.la` module is defined.

State and persistence: build-only metadata; it creates no runtime state and persists no generated files beyond normal Automake outputs.

Dependencies and integration: integrates with GlusterFS's recursive build layout. Its only dependency is the presence of the `src` subdirectory.

Risks and test signals: low risk, but omission from a parent `SUBDIRS` list or a missing `src` directory would prevent `nl-cache` from building. Build validation should include `make`/`make distcheck` coverage that confirms recursive descent.
