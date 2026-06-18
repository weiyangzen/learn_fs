# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/driver.h

## Purpose

This header declares the native SGX driver interface shared by the SGX misc-device, ioctl, and core files.

## Important APIs, Types, And Functions

It defines EINIT retry constants `SGX_EINIT_SPIN_COUNT`, `SGX_EINIT_SLEEP_COUNT`, and `SGX_EINIT_SLEEP_TIME`. It declares reserved masks for SGX attributes, XFRM, and miscselect; `sgx_provision_fops`; `sgx_ioctl()`; and `sgx_drv_init()`.

## Control Flow

The header itself has no flow. The constants drive retry/sleep behavior in EINIT ioctl handling, and prototypes connect file operations to ioctl implementation.

## State, Dependencies, And Integration

It depends on kref, mmu_notifier, scheduler/workqueue headers, SGX UAPI definitions, and `sgx.h`. It integrates the native driver with provisioning and enclave ioctl code.

## Risks And Test Signals

Changing retry constants changes EINIT latency and interrupt responsiveness. Prototype or include drift breaks SGX builds. Test through SGX native driver builds and EINIT behavior under signals/interrupts.
