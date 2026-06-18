# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/imx-vdoa.h

## Purpose
`imx-vdoa.h` is the public integration header for the optional i.MX VDOA helper. It lets CODA code compile both with and without `CONFIG_VIDEO_IMX_VDOA` by exposing real function prototypes when the driver is enabled and harmless inline stubs when it is not.

## Important APIs and Types
The header forward-declares `struct vdoa_data` and `struct vdoa_ctx`, keeping the implementation opaque. The API surface is `vdoa_context_create`, `vdoa_context_configure`, `vdoa_context_destroy`, `vdoa_device_run`, and `vdoa_wait_for_completion`. The enabled configuration expects `u32` pixel formats and `dma_addr_t` buffer addresses from the including context.

## Control Flow and Integration
CODA users can probe for VDOA availability by calling `vdoa_context_create`; when the config is disabled it returns `NULL`. Format validation can be performed through `vdoa_context_configure`, which returns success in the stub case so callers must separately handle a missing context if VDOA is required for a specific path.

## State and Persistence
The header itself owns no state. In the enabled path, state lives in the opaque context allocated by `imx-vdoa.c`. In the disabled path there is no persistent state, and all operations are no-ops.

## Dependencies and Risks
The conditional depends on `CONFIG_VIDEO_IMX_VDOA` or module form being visible to the preprocessor. The main risk is that stub `vdoa_context_configure` and `vdoa_wait_for_completion` return success, which is appropriate for optional acceleration but can mask accidental use of a missing context if call sites do not check the context pointer.

## Test Signals
Build coverage is the main signal: compile CODA with VDOA built-in, as a module, and disabled. Runtime tests should verify fallback behavior when `vdoa_context_create` returns `NULL` and successful reordering when the real platform device is present.
