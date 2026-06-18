# sources/distributed-fs/ceph-client/include/uapi/drm/etnaviv_drm.h

## Purpose

`etnaviv_drm.h` defines the DRM UAPI for Etnaviv Vivante GPU drivers. It exposes GPU parameter queries, GEM allocation and mmap metadata, CPU/GPU synchronization, command-stream submission with relocation or softpin support, explicit fence fd integration, userptr import, buffer waits, and performance monitor enumeration.

## Important APIs, Types, And Constants

The header states key ABI rules: use `__u64` for pointers, keep fields aligned, and append new fields only when zero has backward-compatible meaning. `struct drm_etnaviv_timespec` is a 32/64-bit-safe absolute monotonic timeout. `ETNAVIV_PARAM_*` constants query model, revision, feature words, stream/register/thread/cache/shader/pixel capabilities, softpin base, product/customer/ECO IDs, and related GPU limits.

GEM structs include `drm_etnaviv_gem_new`, `drm_etnaviv_gem_info`, `drm_etnaviv_gem_cpu_prep`, `drm_etnaviv_gem_cpu_fini`, `drm_etnaviv_gem_userptr`, and `drm_etnaviv_gem_wait`. Submit structs include reloc entries, BO table entries with `presumed` GPU addresses, performance monitor requests, and `drm_etnaviv_gem_submit`. Submit flags cover no implicit sync, fence fd in/out, and softpin. Wait and PM APIs are `drm_etnaviv_wait_fence`, `drm_etnaviv_pm_domain`, and `drm_etnaviv_pm_signal`.

## Control Flow

Userspace queries parameters per pipe, creates GEM buffers, gets mmap offsets, uses CPU prep/fini around CPU access, then submits command streams. Reloc-based submits require relocation entries sorted by increasing `submit_offset`; the kernel patches command addresses from referenced BO GPU addresses. Softpin submits interpret `presumed` as fixed GPU VA, shifting address-space management to userspace. Synchronization flows through implicit BO dependencies or explicit sync-file FDs and fence waits.

## State And Persistence

GEM handles persist for the DRM file lifetime; userptr handles pin user memory while valid. The kernel tracks GPU mappings, fences, sequence numbers, command parser state, performance monitor readbacks, and CPU prep state. `presumed` addresses are cacheable hints unless softpin makes them requested fixed addresses.

## Dependencies And Integration Points

The file includes `drm.h` and integrates with DRM GEM, mmap offsets, scheduler/fence infrastructure, dma-fence/sync-file, Etnaviv GPU MMU, and Mesa's Etnaviv Gallium driver.

## Risks

Unsorted relocations should be rejected. Softpin can fail on VA conflicts and places correctness burden on userspace. Cache flags and CPU prep/fini must be respected to avoid stale data. Absolute timeouts require monotonic time. Userptr mappings must validate page alignment and lifetime. Fence sequence numbers are per pipe and should not be treated as global ordering.

## Test Signals

Tests should cover get-param for supported pipes, GEM flags/mmap offsets, CPU prep/fini modes, valid and invalid submit BO tables, unsorted reloc rejection, softpin collision behavior, explicit fence fd in/out, wait timeout/nonblock behavior, userptr alignment validation, PM domain/signal enumeration, and 32-bit ABI layout checks.
