# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/sgx.h

## Purpose

This header defines SGX EPC core structures, constants, and cross-file APIs shared by native SGX, enclave management, reclaim, and KVM virtual EPC support.

## Important APIs, Types, And Functions

Important constants include EPC section limits, EEXTEND block size, reclaim scan/watermark values, and EPC page flags. Types include `struct sgx_epc_page`, `struct sgx_numa_node`, and `struct sgx_epc_section`. Inline helpers `sgx_get_epc_phys_addr()` and `sgx_get_epc_virt_addr()` map an EPC page descriptor to physical/virtual addresses. Prototypes cover EPC allocation/free, reclaim tracking, IPI callback, vEPC init, usage counting, and launch public-key hash updates.

## Control Flow

The header only contains address-computation helpers. They locate the owning section, compute the page-array index, and derive the physical or remapped virtual EPC address.

## State, Dependencies, And Integration

It exposes `sgx_epc_sections[]` and core APIs implemented in `main.c`. Dependencies include SGX architectural definitions, bitops, I/O, and x86 assembly headers. It integrates every SGX implementation file and provides stubs for non-KVM builds.

## Risks And Test Signals

Address computations rely on page descriptors belonging to the correct section arrays. Flag definitions coordinate allocator and reclaimer ownership. Test by exercising native enclave allocation/free, reclaim, poisoned pages, and KVM vEPC with `CONFIG_X86_SGX_KVM` both enabled and disabled.
