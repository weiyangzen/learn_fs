# sources/distributed-fs/ceph-client/samples/workqueue/stall_detector/Makefile

## Purpose
This kbuild fragment declares the `wq_stall` kernel module sample.

## APIs, Types, And Functions
It uses `obj-m += wq_stall.o`, making `wq_stall.c` build as an external-style loadable module under the kernel samples tree.

## Control Flow
Kbuild compiles and links `wq_stall.o` into `wq_stall.ko` when this sample directory is built.

## State And Persistence
No runtime state exists in the Makefile. Module artifacts are produced by kbuild.

## Dependencies And Integration Points
It integrates with kernel module build rules and the workqueue stall detector sample.

## Risks And Test Signals
Risks are limited to module build compatibility. Test signal is successful `wq_stall.ko` creation.
