# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/Makefile

## Purpose

This Makefile selects x86 SGX support objects. It builds the native SGX device driver, enclave backing/fault logic, ioctl handlers, EPC page-cache core, and optional KVM virtual EPC support.

## Important APIs, Types, And Functions

Always-built objects are `driver.o`, `encl.o`, `ioctl.o`, and `main.o`. `virt.o` is included when `CONFIG_X86_SGX_KVM` is enabled.

## Control Flow

There is no runtime control flow. Kconfig determines whether the KVM-facing `/dev/sgx_vepc` and exported virtualization ENCLS helpers are included.

## State, Dependencies, And Integration

This file controls link composition for SGX and KVM integration. It depends on the kernel build system and SGX Kconfig options.

## Risks And Test Signals

Missing objects produce unresolved symbols or absent devices. Test base SGX builds and SGX+KVM builds, then verify `/dev/sgx_enclave`, `/dev/sgx_provision`, and optional `/dev/sgx_vepc` registration behavior.
