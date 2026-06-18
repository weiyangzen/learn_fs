<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.h

## Purpose

`xe_svm.h` declares the SVM, devmem pagemap, and SVM range API, with full implementations when `CONFIG_DRM_XE_GPUSVM` is enabled and stub fallbacks otherwise.

## Important APIs, Types, and Functions

With GPU SVM enabled, the header defines `struct xe_svm_range`, `struct xe_pagemap`, range helpers, lifecycle functions, pagefault handling, range migration/validation, PTE zap, pagemap resolution, pagemap shrinker/cache creation, and `xe_drm_pagemap_from_fd()`. It also defines interconnect protocol IDs for local VRAM and P2P. Without GPU SVM, it provides stub structures and no-op or error-returning inline functions.

## Control Flow

Callers can compile against a single interface regardless of config. Runtime paths use notifier lock helpers (`xe_svm_notifier_lock`, unlock, asserts) when DRM GPUSVM exists, and no-op lock helpers otherwise.

## State and Persistence Behavior

The full structs persist in VM and pagemap state. The fallback range struct preserves enough fields for code to compile but reports no valid pages/mappings.

## Dependencies and Integration Points

The full path depends on DRM GPU SVM, DRM pagemap, Xe VM, BO, GT, tile, VMA, and VRAM types. Integration points span VM fault handling, VMA memory attributes, device memory fd handling, and tile pagemap cache setup.

## Risks and Test Signals

The fallback signature for `xe_svm_range_validate()` differs semantically from the full declaration and should be watched during config-matrix builds. Tests should compile both GPUSVM/pagemap enabled and disabled configurations and exercise inline helpers for range boundaries and DMA mapping visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.h -->
