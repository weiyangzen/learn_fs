# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_drv.c

## Purpose

`malidp_drv.c` is the top-level ARM Mali-DP KMS/DRM platform driver. It allocates the DRM device and hardware runtime state, validates the detected IP variant against device-tree, sets up clocks, reserved memory, mode-config, CRTC, planes, writeback, components, IRQs, vblank, PM, debugfs, framebuffer creation, and the custom atomic commit tail.

## Important APIs, Types, And Functions

Key structures are `malidp_driver`, `malidp_mode_config_funcs`, `malidp_mode_config_helpers`, `malidp_drm_of_match`, `malidp_pm_ops`, and `malidp_platform_driver`. Important functions include `malidp_bind()`, `malidp_unbind()`, `malidp_atomic_commit_tail()`, `malidp_set_and_wait_config_valid()`, `malidp_fb_create()`, AFBC framebuffer verification helpers, `malidp_irq_init()`, `malidp_dumb_create()`, runtime PM callbacks, and debugfs error-stat helpers.

## Control Flow

Probe finds an OF output endpoint and registers a component master. Bind allocates `struct malidp_drm`, allocates `struct malidp_hw_device`, maps MMIO, gets pclk/aclk/mclk/pxlclk, attaches optional reserved memory, enables runtime PM, verifies DT compatible string and resource size against hardware ID, queries variant capabilities, programs output color depth and ARQOS, initializes config-valid state and waitqueue, initializes mode config/CRTC/writeback, binds the encoder component, sets possible-clone masks, installs DE/SE IRQs, initializes vblank, registers the DRM device, and starts client setup. The commit tail gets runtime PM, clears config-valid, applies modeset disables, writes gamma/color/scaling state, commits active planes, commits writeback, enables modesets, waits for config-valid completion, releases PM, and cleans planes.

## State And Persistence Behavior

Persistent driver state lives in `struct malidp_drm` and `struct malidp_hw_device`: hardware callbacks, MMIO, clocks, output color depth, runtime PM suspend flag, config-valid atomic, waitqueue, pending event pointer, error statistics, core ID, and memory-write state. Hardware state includes coefficient tables, display function bits, scaling engine registers, plane registers, config-valid flag, output depth, IRQ masks, and clocks. AFBC framebuffer validation checks buffer size and layout before framebuffer creation.

## Dependencies And Integration Points

The file integrates DRM atomic helpers, DRM GEM DMA/fbdev helpers, component framework, OF graph/device matching, reserved memory, runtime/system PM, clocks, debugfs, Mali-DP hardware tables, CRTC/plane initialization, memory writeback, and DE/SE IRQ helpers. Device-tree properties include compatibles, `arm,malidp-arqos-value`, and `arm,malidp-output-port-lines`.

## Risks And Edge Cases

Config-valid wait can time out and retries only five times before logging. Runtime PM transitions must not occur outside config mode. Hardware-ID and resource-size validation are variant-sensitive because DP500 uses different register locations. AFBC verification assumes 16x16 superblocks and one GEM object, checks pitch against width*bpp, and only supports a subset of modifiers. Error unwinding must balance PM, component binding, IRQs, reserved memory, and OF references.

## Test Signals

Important tests include probe on DP500/DP550/DP650 DTs, DT/hardware mismatch rejection, insufficient resource-size rejection, output-port-lines parsing, ARQOS programming, atomic commit event delivery through config-valid IRQ, AFBC framebuffer validation success/failure, runtime/system suspend-resume, debugfs error-stat reset/read, writeback atomic commits, vblank init, and component bind failure unwinding.
