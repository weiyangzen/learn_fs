# sources/distributed-fs/ceph-client/scripts/ipe/Makefile

## Purpose
Registers the IPE scripts subdirectory for host build traversal.

## APIs, Control Flow, and State
The Makefile contains `subdir-y := polgen`, causing kbuild to descend into `scripts/ipe/polgen`. It has no runtime behavior or mutable state.

## Dependencies and Integration
It depends on kbuild subdir processing and integrates the IPE policy generator into the scripts host-tool build.

## Risks and Test Signals
The only practical risk is accidentally omitting `polgen` from host builds. Test signals are `scripts/ipe/polgen/polgen` being built when the scripts tree is processed.
