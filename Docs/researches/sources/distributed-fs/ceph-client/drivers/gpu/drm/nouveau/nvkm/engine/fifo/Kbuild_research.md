<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/Kbuild

## Purpose

`fifo/Kbuild` lists all nouveau FIFO engine sources built into `nvkm-y`.

## Important APIs, Types, And Functions

It includes shared infrastructure (`base.o`, `cgrp.o`, `chan.o`, `chid.o`, `runl.o`, `runq.o`), legacy through modern generation backends (`nv04.o` through `gb202.o`), and user object wrappers (`ucgrp.o`, `uchan.o`).

## Control Flow

There is no runtime control flow. The build system uses this list so all referenced FIFO generation constructors and shared helpers are linked.

## State And Persistence Behavior

No runtime state is stored. The file controls build-time availability.

## Dependencies And Integration Points

It integrates with the parent nouveau Kbuild and the full FIFO subsystem.

## Risks And Edge Cases

Omitting a backend can cause link failures or missing support for a chipset. New generation support must add implementation and Kbuild entries together.

## Test Signals

Kernel build success and successful probe across FIFO generations are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/Kbuild -->
