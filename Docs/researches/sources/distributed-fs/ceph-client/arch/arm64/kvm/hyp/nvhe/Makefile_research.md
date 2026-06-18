# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/Makefile

## Purpose

This Makefile builds the nVHE hypervisor object as isolated `.nvhe.o` files, links them with a hyp linker script, generates runtime relocation metadata, and prefixes symbols for final linking into `vmlinux`.

## Important APIs, Types, And Functions

Important variables are `asflags-y`, `ccflags-y`, `hyp-obj-y`, `hyp-obj`, `targets`, `LDFLAGS_kvm_nvhe.tmp.o`, and `LDFLAGS_kvm_nvhe.rel.o`. Build commands include `cc_o_c`, `as_o_S`, `cpp_lds_S`, `ld`, `hyprel`, and `hypcopy`.

## Control Flow

The build compiles sources to `.nvhe.o`, preprocesses `hyp.lds`, partially links objects into `kvm_nvhe.tmp.o`, runs `gen-hyprel` to create relocation assembly, links relocations into `kvm_nvhe.rel.o`, and uses objcopy to prefix symbols with `__kvm_nvhe_`.

## State And Persistence Behavior

The file creates build artifacts, not runtime state. It also removes ftrace, SCS, unwind, async unwind, and some profiling flags for isolated hyp code.

## Dependencies And Integration Points

It includes shared hyp objects, lib routines, SMCCC call code, optional tracing, optional hardened list debug, and optional UBSAN trap mode.

## Risks And Test Signals

Risks are relocation-generation failures, symbol collisions, forbidden instrumentation entering hyp code, missing shared objects, and unsupported LLVM SHT_REL profile sections. Test signals are successful `kvm_nvhe.o` generation, prefixed symbols, no ftrace/SCS instrumentation, and UBSAN/trace configuration builds.
