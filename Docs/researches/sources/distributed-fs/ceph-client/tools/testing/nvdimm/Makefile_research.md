# sources/distributed-fs/ceph-client/tools/testing/nvdimm/Makefile

## Purpose
This Makefile provides a simple external-module entry point for building and installing the nvdimm test modules against a kernel tree.

## Important APIs, Types, And Functions
Build targets are `default` and `install`. `KDIR ?= ../../../` defaults the kernel source/build directory to the repository root relative to this tool directory.

## Control Flow
`default` invokes `$(MAKE) -C $(KDIR) M=$$PWD`, asking kbuild to build the current directory as an external module. `install` first builds, then invokes `modules_install` for the same module directory.

## State And Persistence
The Makefile itself holds no runtime state. The `install` target persists built modules into the kernel module install tree selected by kbuild.

## Dependencies And Integration Points
It depends on a kernel build tree that can process the local `Kbuild` file. It is a developer convenience wrapper around kbuild rather than part of the in-kernel module dependency graph.

## Risks
The default `KDIR` assumes the current repository layout. Invoking from unusual working directories is safe because `M=$$PWD` expands in the shell, but a wrong `KDIR` will build against the wrong tree or fail.

## Test Signals
A successful `make` proves kbuild can compile the module set. A successful `make install` additionally proves module installation permissions and paths are valid.
