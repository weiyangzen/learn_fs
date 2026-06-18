# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/Makefile

Purpose: declares the 68060 integer and floating-point support package wrapper objects for the m68k kernel build.

Important APIs/types/functions: `obj-y := fskeleton.o iskeleton.o os.o` builds the FPSP wrapper, ISP wrapper, and shared operating-system call-outs.

Control flow: build-system only. Kbuild links these objects when the 68060 support package directory is selected.

State and persistence: no runtime state.

Dependencies/integration: integrates Linux Kbuild with `fskeleton.S`, `iskeleton.S`, and `os.S`; those include generated/converted Motorola package sources (`fpsp.sa`, `isp.sa`) at assembly time.

Risks: missing any of the three objects breaks call-out table references or package entry symbols. Object ordering can matter if included package labels rely on local wrapper symbols.

Test signals: 68060 m68k build, resolution of `_060_fpsp_*`, `_060_isp_*`, and `_060_[id]mem_*` symbols, and successful assembly of included `.sa` package files.
